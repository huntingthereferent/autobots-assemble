"""Finite example of local pinned-object identity, not remote authentication.

Only models already admitted local in-process evidence. A remote source label,
matching digest, or issued token is not proof of a real-world source identity.
"""
from dataclasses import dataclass
from secrets import token_hex


@dataclass(frozen=True)
class Snapshot:
    source_label: str
    revision: int
    digest: str


@dataclass(frozen=True)
class Description:
    token: str
    source_label: str
    revision: int
    digest: str
    predecessor: str | None


@dataclass
class Record:
    owner: object
    snapshot: Snapshot
    description: Description
    active: bool = True


class Ledger:
    """Caller must have authenticated/verified owner binding elsewhere."""
    def __init__(self):
        self.records: dict[str, Record] = {}

    def issue_from_verified_local_binding(self, owner, snapshot, *, predecessor=None):
        if owner is None or type(snapshot) is not Snapshot:
            raise ValueError('locally held owner and snapshot are required')
        if predecessor is not None and predecessor not in self.records:
            raise ValueError('unknown previous pin')
        # Does not authenticate the arguments: only the trusted local caller
        # may invoke issuance after checking its live owner binding.
        description=Description(token_hex(24),snapshot.source_label,
                 snapshot.revision,snapshot.digest,predecessor)
        self.records[description.token]=Record(owner,snapshot,description)
        return description

    def check(self, token, owner, snapshot):
        record=self.records.get(token)
        if record is None or not record.active:
            return False
        expected=record.description
        valid=(owner is record.owner and snapshot is record.snapshot and
               (snapshot.source_label,snapshot.revision,snapshot.digest)==
               (expected.source_label,expected.revision,expected.digest))
        if not valid:
            record.active=False
        return valid

    def revoke(self, token):
        if token not in self.records:
            raise ValueError('unknown pin')
        self.records[token].active=False


if __name__=='__main__':
    ledger=Ledger()
    owner=object()
    snap=Snapshot('example',0,'a'*64)
    pin=ledger.issue_from_verified_local_binding(owner,snap)
    copy=Snapshot(snap.source_label,snap.revision,snap.digest)
    print('same issued objects:',ledger.check(pin.token,owner,snap))
    print('copied metadata on new snapshot:',ledger.check(pin.token,owner,copy))
    print('old pin remains revoked:',ledger.check(pin.token,owner,snap))
