"""Optional encrypted native HandoffRuntime journal, not a key vault.

The encryption key is supplied by a trusted host. Neither local SQLite nor
the cipher protects against database rollback, compromised hosts, or
unauthorized use of an already-running process.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from contextlib import closing
import json
import os
import sqlite3
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from runtime.journal import RuntimeJournal
from .continuation import DIGEST, TOKEN, EnvelopeError

SCHEMA = b"ab-native-sealed-journal/v1"
SENTINEL = b"native-journal-key-check/v1"
MAX_RECORD = 1_048_576
ZERO = b"\x00" * 32


class SealedJournalError(ValueError):
    """Key mismatch, damaged encrypted record, or unsafe store."""


class SealedRuntimeJournal(RuntimeJournal):
    """Same native append/replay contract; encrypted SQLite records on disk.

    Requires a single trusted writer. Append is committed before native
    HandoffRuntime mutates its in-memory state. Missing-middle-row and
    tampered-ciphertext checks cannot detect total rollback/truncation.
    """

    def __init__(self, path: str | Path, *, key: bytes) -> None:
        self.path = Path(path)
        if type(key) is not bytes or len(key) != 32:
            raise SealedJournalError("host-supplied 32-byte journal key required")
        if self.path.is_symlink() or not self.path.parent.is_dir() or self.path.is_dir():
            raise SealedJournalError("unsafe sealed journal path")
        self._crypto = AESGCM(key)
        self._handoffs = {}
        self._events = []
        if not self.path.exists():
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                pass
            else:
                os.close(fd)
        if self.path.is_symlink() or not self.path.is_file():
            raise SealedJournalError("unsafe sealed journal storage")
        with closing(self._connect()) as db:
            db.execute("CREATE TABLE IF NOT EXISTS seal (version TEXT PRIMARY KEY, nonce BLOB NOT NULL, proof BLOB NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS records (seq INTEGER PRIMARY KEY, prev BLOB NOT NULL, nonce BLOB NOT NULL, cipher BLOB NOT NULL, digest BLOB NOT NULL)")
            # An earlier draft database might contain signed ingress records
            # admitted to a SEPARATE ledger. Refuse silent conversion that
            # would forget those old replay decisions.
            already_admitted = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='admitted'").fetchone()
            if not already_admitted and db.execute("SELECT 1 FROM records LIMIT 1").fetchone():
                raise SealedJournalError("legacy sealed history needs explicit replay-ledger migration")
            db.execute("CREATE TABLE IF NOT EXISTS admitted (token BLOB PRIMARY KEY, digest BLOB NOT NULL)")
            row = db.execute("SELECT version, nonce, proof FROM seal").fetchall()
            if not row:
                if db.execute("SELECT 1 FROM records LIMIT 1").fetchone():
                    raise SealedJournalError("unsealed existing journal")
                nonce = os.urandom(12)
                db.execute("INSERT INTO seal VALUES (?, ?, ?)",
                           (SCHEMA.decode("ascii"), nonce,
                            self._crypto.encrypt(nonce, SENTINEL, SCHEMA)))
                db.commit()
                row = db.execute("SELECT version, nonce, proof FROM seal").fetchall()
            if len(row) != 1 or row[0][0] != SCHEMA.decode("ascii"):
                raise SealedJournalError("unexpected journal format")
            try:
                if self._crypto.decrypt(row[0][1], row[0][2], SCHEMA) != SENTINEL:
                    raise SealedJournalError("wrong encrypted journal key")
            except (InvalidTag, ValueError) as exc:
                raise SealedJournalError("wrong key or damaged journal header") from exc
            previous = ZERO
            expected_seq = 1
            protected_admissions = {}
            for seq, prev, nonce, cipher, digest in db.execute(
                    "SELECT seq, prev, nonce, cipher, digest FROM records ORDER BY seq"):
                if seq != expected_seq or prev != previous or len(nonce) != 12:
                    raise SealedJournalError("encrypted journal chain interrupted")
                if digest != self._digest(seq, prev, nonce, cipher):
                    raise SealedJournalError("encrypted journal record altered")
                try:
                    plain = self._crypto.decrypt(nonce, cipher, self._aad(seq, prev))
                except (InvalidTag, ValueError) as exc:
                    raise SealedJournalError("encrypted journal record failed authentication") from exc
                if not 0 < len(plain) <= MAX_RECORD:
                    raise SealedJournalError("invalid decrypted record size")
                try:
                    record = json.loads(plain.decode("utf-8"))
                    protected = record.get("_sealed_admission")
                    if protected is not None:
                        if (type(protected) is not dict
                                or set(protected) != {"token", "digest"}
                                or type(protected["token"]) is not str
                                or len(protected["token"]) != 64
                                or type(protected["digest"]) is not str
                                or not DIGEST.fullmatch(protected["digest"])):
                            raise SealedJournalError("invalid encrypted replay identity")
                        token = bytes.fromhex(protected["token"])
                        if token in protected_admissions:
                            raise SealedJournalError("duplicate encrypted replay identity")
                        protected_admissions[token] = bytes.fromhex(protected["digest"])
                    self._replay(record, line_number=seq)
                except (UnicodeError, ValueError, TypeError, KeyError) as exc:
                    raise SealedJournalError("invalid decrypted runtime record") from exc
                previous = digest
                expected_seq += 1
            actual_admissions = dict(db.execute("SELECT token, digest FROM admitted"))
            if actual_admissions != protected_admissions:
                raise SealedJournalError("replay table differs from authenticated native history")
            self._committed_records = expected_seq - 1

    def _connect(self):
        if self.path.is_symlink():
            raise SealedJournalError("journal path became a symlink")
        db = sqlite3.connect(self.path, timeout=10)
        db.execute("PRAGMA secure_delete=ON")
        return db

    @staticmethod
    def _aad(seq: int, prev: bytes) -> bytes:
        return SCHEMA + b"|" + seq.to_bytes(8, "big") + b"|" + prev

    @classmethod
    def _digest(cls, seq: int, prev: bytes, nonce: bytes, cipher: bytes) -> bytes:
        return sha256(cls._aad(seq, prev) + nonce + cipher).digest()

    @staticmethod
    def _admission_token(lane: str, event_id: str) -> bytes:
        if not isinstance(lane, str) or not TOKEN.fullmatch(lane) or not isinstance(event_id, str) or not TOKEN.fullmatch(event_id):
            raise EnvelopeError("invalid native admission scope")
        return sha256(b"ab-sealed-admission/v1\\0" + lane.encode("ascii") +
                      b"\\0" + event_id.encode("ascii")).digest()

    def require_new(self, lane: str, event_id: str) -> None:
        """Early replay refusal; UNIQUE constraint is the final atomic guard."""
        token = self._admission_token(lane, event_id)
        with closing(self._connect()) as db:
            if db.execute("SELECT 1 FROM admitted WHERE token=?", (token,)).fetchone():
                raise EnvelopeError("replayed or reused event identifier")

    def _after_replay_insert(self) -> None:
        """Test fault-injection point inside the uncommitted transaction."""
        return None

    def _after_record_insert(self) -> None:
        """Test fault-injection point after native row, before SQLite commit."""
        return None

    def _append_admitted_record(self, record: dict, admission: tuple[str, str, str]) -> None:
        self._append_record(record, admission=admission)

    def _append_record(self, record: dict, *, admission: tuple[str, str, str] | None = None) -> None:
        token = None
        signed_digest = None
        if admission is not None:
            if type(admission) is not tuple or len(admission) != 3:
                raise EnvelopeError("invalid native replay admission")
            lane, event_id, envelope_sha = admission
            token = self._admission_token(lane, event_id)
            if not isinstance(envelope_sha, str) or not DIGEST.fullmatch(envelope_sha):
                raise EnvelopeError("invalid envelope digest")
            signed_digest = bytes.fromhex(envelope_sha)
            if "_sealed_admission" in record:
                raise SealedJournalError("internal replay metadata must not be caller supplied")
            record = {**record, "_sealed_admission":
                      {"token": token.hex(), "digest": envelope_sha}}
        try:
            raw = json.dumps(record, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("ascii")
        except (TypeError, ValueError) as exc:
            raise SealedJournalError("invalid runtime record") from exc
        if not 0 < len(raw) <= MAX_RECORD:
            raise SealedJournalError("unbounded runtime record")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT seq, digest FROM records ORDER BY seq DESC LIMIT 1").fetchone()
            seq, previous = ((row[0] + 1, row[1]) if row else (1, ZERO))
            if seq != self._committed_records + 1:
                raise SealedJournalError("concurrent journal writer detected; restart required")
            if token is not None:
                try:
                    db.execute("INSERT INTO admitted VALUES (?, ?)", (token, signed_digest))
                except sqlite3.IntegrityError as exc:
                    raise EnvelopeError("replayed or reused event identifier") from exc
                # A crash here rolls back admission as well as native movement.
                self._after_replay_insert()
            nonce = os.urandom(12)
            cipher = self._crypto.encrypt(nonce, raw, self._aad(seq, previous))
            db.execute("INSERT INTO records VALUES (?, ?, ?, ?, ?)",
                       (seq, previous, nonce, cipher,
                        self._digest(seq, previous, nonce, cipher)))
            self._after_record_insert()
            db.commit()
            self._committed_records += 1
