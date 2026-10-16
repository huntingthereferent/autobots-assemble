"""B14: explicit local-operator Ed25519 pin lifecycle for B13/B11 delivery.

Only PUBLIC key digests and operator-provided labels are recorded. Operator
authorization is an EXTERNAL decision: a hash-chained local audit file does
NOT authenticate a human, issue a credential, or establish legal source
ownership. Exactly one process may write the ledger at a time.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path

from .b12_b3_native_delivery import B3NativeLocalSource, SOURCE_NAME
from .b13_offline_owner_delivery import B13OfflineOwnerDelivery, load_operator_pin

SCHEMA = "b14-operator-pinned-source-key/v1"
_MAX_BYTES = 200_000
_ROW_KEYS = frozenset(("schema", "sequence", "previous_hash", "kind", "source_name",
                       "source_edition", "pin_sha256", "prior_sha256", "operator_ref",
                       "verification_ref", "record_hash"))
_DIGEST = set("0123456789abcdef")


def _valid_id(s: object) -> bool:
    return isinstance(s, str) and 0 < len(s) <= 200 and s.strip() == s


def _valid_digest(s: object) -> bool:
    return isinstance(s, str) and len(s) == 64 and all(c in _DIGEST for c in s)


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _reject_duplicates(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicated operator pin journal key")
        result[key] = value
    return result


class OperatorPinLedger:
    """Local hash-chained, single-writer policy with explicit operator commands.

    Enrollment requires independently checked public-key bytes/digest. A prior
    key may NEVER be reactivated for the same source and edition. Rotation
    retains the source-edition relation, not an assertion of a new B3 edition.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _read(self) -> tuple[list[dict], dict[tuple[str, str], str]]:
        path = self.path
        if not path.exists():
            return [], {}
        if (path.is_symlink() or not path.is_file()
                or path.stat().st_size > _MAX_BYTES):
            raise ValueError("operator pin journal is unsafe")
        blob = path.read_bytes()
        if not blob.endswith(b"\n") and blob:
            raise ValueError("incomplete operator pin record")
        if len(blob) > _MAX_BYTES:
            raise ValueError("operator pin journal over size limit")
        rows = []
        active: dict[tuple[str, str], str] = {}
        used: dict[tuple[str, str], set[str]] = {}
        prior = None
        for index, line in enumerate(blob.splitlines(), 1):
            try:
                row = json.loads(line, object_pairs_hook=_reject_duplicates)
            except (ValueError, UnicodeError) as exc:
                raise ValueError("operator pin journal has malformed JSON") from exc
            if (not isinstance(row, dict) or set(row) != _ROW_KEYS
                    or row.get("schema") != SCHEMA
                    or type(row["sequence"]) is not int or row["sequence"] != index
                    or row["previous_hash"] != prior
                    or row["kind"] not in ("ENROLL", "ROTATE", "REVOKE")
                    or not _valid_id(row["source_name"])
                    or not _valid_id(row["source_edition"])
                    or not _valid_id(row["operator_ref"])
                    or not _valid_id(row["verification_ref"])
                    or not _valid_digest(row["pin_sha256"])
                    or (row["prior_sha256"] is not None
                        and not _valid_digest(row["prior_sha256"]))
                    or not _valid_digest(row["record_hash"])
                    or row["record_hash"] != sha256(_canonical({
                        k: v for k, v in row.items() if k != "record_hash"
                    })).hexdigest()):
                raise ValueError("operator pin journal identity or chain invalid")
            key = (row["source_name"], row["source_edition"])
            old = active.get(key)
            known = used.setdefault(key, set())
            kind = row["kind"]
            if kind == "ENROLL":
                if old is not None or row["prior_sha256"] is not None or row["pin_sha256"] in known:
                    raise ValueError("operator pin enrollment conflicts with existing history")
                active[key] = row["pin_sha256"]
                known.add(row["pin_sha256"])
            elif kind == "ROTATE":
                if (old is None or row["prior_sha256"] != old
                        or row["pin_sha256"] == old or row["pin_sha256"] in known):
                    raise ValueError("rotation must replace one exact active unused key")
                active[key] = row["pin_sha256"]
                known.add(row["pin_sha256"])
            else:
                if old is None or row["prior_sha256"] != old or row["pin_sha256"] != old:
                    raise ValueError("revocation must target one exact active pin")
                active.pop(key)
            rows.append(row)
            prior = row["record_hash"]
        return rows, active

    def history(self) -> tuple[dict, ...]:
        rows, _ = self._read()
        return tuple(dict(x) for x in rows)

    def current(self, source_name: str, source_edition: str) -> str | None:
        if not _valid_id(source_name) or not _valid_id(source_edition):
            raise ValueError("exact source and edition required")
        _, active = self._read()
        return active.get((source_name, source_edition))

    def is_current(self, source_name: str, source_edition: str, pin_sha256: str) -> bool:
        return (_valid_digest(pin_sha256)
                and self.current(source_name, source_edition) == pin_sha256)

    def require_current(self, source_name: str, source_edition: str,
                        pin_sha256: str) -> None:
        if not self.is_current(source_name, source_edition, pin_sha256):
            raise PermissionError("operator source signing pin revoked, rotated or absent")

    def _append(self, kind: str, *, source_name: str, source_edition: str,
                pin_sha256: str, prior_sha256: str | None,
                operator_ref: str, verification_ref: str) -> dict:
        if (not all(_valid_id(x) for x in (
                source_name, source_edition, operator_ref, verification_ref))
                or not _valid_digest(pin_sha256)
                or (prior_sha256 is not None and not _valid_digest(prior_sha256))):
            raise ValueError("exact operator pin admission fields required")
        rows, active = self._read()
        key = (source_name, source_edition)
        old = active.get(key)
        used = {x["pin_sha256"] for x in rows
                if (x["source_name"], x["source_edition"]) == key}
        if kind == "ENROLL":
            if old is not None or prior_sha256 is not None or pin_sha256 in used:
                raise ValueError("pin already active or historically enrolled")
        elif kind == "ROTATE":
            if old is None or old != prior_sha256 or pin_sha256 in used:
                raise ValueError("pin rotation must replace the confirmed active pin")
        elif kind == "REVOKE":
            if old is None or old != prior_sha256 or pin_sha256 != old:
                raise ValueError("pin revocation must confirm the exact active pin")
        else:
            raise ValueError("unknown pin ledger operation")
        data = {
            "schema": SCHEMA, "sequence": len(rows) + 1,
            "previous_hash": rows[-1]["record_hash"] if rows else None,
            "kind": kind, "source_name": source_name,
            "source_edition": source_edition, "pin_sha256": pin_sha256,
            "prior_sha256": prior_sha256, "operator_ref": operator_ref,
            "verification_ref": verification_ref,
        }
        row = {**data, "record_hash": sha256(_canonical(data)).hexdigest()}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.is_symlink():
            raise ValueError("operator pin journal cannot be a symlink")
        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(self.path, flags, 0o600)
        try:
            os.write(fd, _canonical(row) + b"\n")
            os.fsync(fd)
        finally:
            os.close(fd)
        self._read()
        return row

    def enroll(self, *, source_name: str, source_edition: str, pin_sha256: str,
               operator_ref: str, verification_ref: str,
               confirm_pin_sha256: str) -> dict:
        if pin_sha256 != confirm_pin_sha256:
            raise PermissionError("operator must independently confirm the exact new pin")
        return self._append("ENROLL", source_name=source_name, source_edition=source_edition,
                            pin_sha256=pin_sha256, prior_sha256=None,
                            operator_ref=operator_ref, verification_ref=verification_ref)

    def rotate(self, *, source_name: str, source_edition: str, prior_sha256: str,
               new_pin_sha256: str, operator_ref: str, verification_ref: str,
               confirm_prior_sha256: str, confirm_new_sha256: str) -> dict:
        if prior_sha256 != confirm_prior_sha256 or new_pin_sha256 != confirm_new_sha256:
            raise PermissionError("operator must confirm both existing and new key fingerprints")
        return self._append("ROTATE", source_name=source_name, source_edition=source_edition,
                            pin_sha256=new_pin_sha256, prior_sha256=prior_sha256,
                            operator_ref=operator_ref, verification_ref=verification_ref)

    def revoke(self, *, source_name: str, source_edition: str, pin_sha256: str,
               operator_ref: str, verification_ref: str,
               confirm_pin_sha256: str) -> dict:
        if pin_sha256 != confirm_pin_sha256:
            raise PermissionError("operator must confirm the exact active key being revoked")
        return self._append("REVOKE", source_name=source_name, source_edition=source_edition,
                            pin_sha256=pin_sha256, prior_sha256=pin_sha256,
                            operator_ref=operator_ref, verification_ref=verification_ref)


class B14OperatorTrustedDelivery:
    """B13 delivery gated on the CURRENT operator pin at every native boundary.

    Policy ledger and public key are independent inputs; an envelope cannot
    enroll/rotate the key, and an old host instance cannot ignore revocation.
    """

    def __init__(self, *, trust_ledger_path: str | Path,
                 public_key_path: str | Path, expected_public_key_sha256: str,
                 construction_dir: str | Path, native_data_dir: str | Path,
                 observed_journal_path: str | Path,
                 lane_handoff_id: str, opening_id: str, job_id: str,
                 confirm_source_job: str):
        self.trust = OperatorPinLedger(trust_ledger_path)
        public_key = load_operator_pin(
            public_key_path, expected_sha256=expected_public_key_sha256,
        )
        source = B3NativeLocalSource(
            data_dir=native_data_dir, lane_handoff_id=lane_handoff_id,
            opening_id=opening_id, job_id=job_id,
        )
        edition = source.inspect().edition_fingerprint
        paths = [
            Path(trust_ledger_path).resolve(), Path(observed_journal_path).resolve(),
            (Path(native_data_dir) / "runtime.jsonl").resolve(),
            (Path(construction_dir) / "runtime.jsonl").resolve(),
            Path(public_key_path).resolve(),
        ]
        if len(set(paths)) != len(paths):
            raise ValueError("operator trust, key, native, construction and observed histories must be separate")
        self.trust.require_current(SOURCE_NAME, edition, expected_public_key_sha256)

        # The B13 constructor now directly reads the same mandatory
        # operator policy, rather than accepting a substitute callback.
        self.host = B13OfflineOwnerDelivery(
            construction_dir=construction_dir, native_data_dir=native_data_dir,
            observed_journal_path=observed_journal_path,
            lane_handoff_id=lane_handoff_id, opening_id=opening_id,
            job_id=job_id, public_key=public_key,
            expected_public_key_sha256=expected_public_key_sha256,
            confirm_source_job=confirm_source_job,
            operator_trust_ledger_path=trust_ledger_path,
        )

    def prepare(self, *, goal_id: str, candidate_id: str, route: tuple[str, ...]) -> str:
        self.host.b12._check_pin()
        return self.host.prepare(goal_id=goal_id, candidate_id=candidate_id, route=route)

    def signing_request(self, request_id: str) -> dict:
        self.host.b12._check_pin()
        return self.host.signing_request(request_id)

    def deliver(self, *, request_id: str, confirm_request: str,
                approved: bool, signed_envelope: dict):
        self.host.b12._check_pin()
        return self.host.deliver(request_id=request_id, confirm_request=confirm_request,
                                 approved=approved, signed_envelope=signed_envelope)
