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
                    self._replay(json.loads(plain.decode("utf-8")), line_number=seq)
                except (UnicodeError, ValueError, TypeError, KeyError) as exc:
                    raise SealedJournalError("invalid decrypted runtime record") from exc
                previous = digest
                expected_seq += 1
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

    def _append_record(self, record: dict) -> None:
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
            nonce = os.urandom(12)
            cipher = self._crypto.encrypt(nonce, raw, self._aad(seq, previous))
            db.execute("INSERT INTO records VALUES (?, ?, ?, ?, ?)",
                       (seq, previous, nonce, cipher,
                        self._digest(seq, previous, nonce, cipher)))
            db.commit()
            self._committed_records += 1
