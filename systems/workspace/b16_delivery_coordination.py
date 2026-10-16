"""B16: cooperative, process-wide operator entry coordination for B13/B14.

Locks stay held BEFORE ObservedEventJournal constructs/replays and through
signed native admission and its resulting journal records. These are local,
advisory, fail-fast OS file locks. A process that bypasses the coordinated
CLI, writes the original B3/B9 journals, or uses a different shared storage
host is not covered by this bounded contract.

Lock files MUST remain in place after release: deleting an advisory lock
inode while another process waits can let two writers hold different locks.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import os
from pathlib import Path
import stat
from threading import local
from typing import Iterator


def _lock_path(journal_path: str | Path) -> Path:
    p = Path(journal_path)
    if p.is_symlink():
        raise ValueError("B16 cannot coordinate a symlinked journal")
    resolved = p.resolve()
    return resolved.with_name(resolved.name + ".b16.lock")


@contextmanager
def _exclusive_file(path: Path) -> Iterator[None]:
    """Acquire one nonblocking local OS lock; never unlink its inode."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("B16 coordination lock cannot be a symlink")
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(path, flags, 0o600)
    locked = False
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise ValueError("B16 coordination lock must be one ordinary file")
        if os.name == "posix":
            import fcntl
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise PermissionError("B16 operator journal busy: another process owns it") from exc
        elif os.name == "nt":
            import msvcrt
            if st.st_size == 0:
                os.write(fd, b"0")
            os.lseek(fd, 0, os.SEEK_SET)
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise PermissionError("B16 operator journal busy: another process owns it") from exc
        else:
            raise RuntimeError("B16 requires an OS-native advisory file lock")
        locked = True
        yield
    finally:
        if locked:
            if os.name == "posix":
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif os.name == "nt":
                import msvcrt
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        os.close(fd)


# Reentrancy is per thread only. A second thread must take the real OS lock,
# including if its owner is in this same process. Nested callers may reuse
# already-held locks but may not extend the set and invert lock ordering.
_OPERATOR_SESSION = local()


@contextmanager
def coordinated_operator_entry(*, trust_ledger: str | Path,
                               observed_journal: str | Path | None = None) -> Iterator[None]:
    """Guard B14 policy writes and B13/B14 native delivery using shared locks.

    The policy lock serializes enrollment/rotation/revocation with **all**
    cooperating native callers using that policy. The observed journal lock
    serializes native callers that target one journal through DIFFERENT policies.
    Ordered locking prevents deadlocks and rejects same-path alias mistakes.
    """
    if trust_ledger is None:
        raise PermissionError("B16 requires an explicit operator trust ledger")
    paths = [_lock_path(trust_ledger)]
    if observed_journal is not None:
        paths.append(_lock_path(observed_journal))
    if len(set(paths)) != len(paths):
        raise ValueError("B16 operator trust and observed journal must be different")
    requested = frozenset(paths)
    held = getattr(_OPERATOR_SESSION, "held", None)
    if held is not None:
        if not requested.issubset(held):
            raise RuntimeError("B17 nested coordination cannot extend a held lock set")
        yield
        return
    with ExitStack() as stack:
        for path in sorted(paths):
            stack.enter_context(_exclusive_file(path))
        _OPERATOR_SESSION.held = requested
        try:
            yield
        finally:
            del _OPERATOR_SESSION.held
