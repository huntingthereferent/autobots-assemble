"""Bounded standalone model of *evidence admission*, not source authentication.

In the full chatbot local provenance depends on live in-process HTTP owner
binding. This model accepts an explicit verifier-controlled owner handle and
checks object identity and pinned revision/digest; source self-claims alone
are never sufficient. It does not observe or independently prove A/B edges.
"""
from dataclasses import dataclass

LOCAL='LOCAL_OWNER_VERIFIED'
REMOTE='REMOTE_ORIGIN_UNVERIFIED'

@dataclass(frozen=True)
class SourceHandle:
    revision: int
    digest: str

@dataclass(frozen=True)
class ProofRequest:
    old_required: bool
    new_required: bool


def verified_scope(*, owner, bound_owner, active: bool, claimed_revision,
                   claimed_digest):
    """Object-identity check; caller must supply genuine owner/binding handles.

    No network or identity authentication is done here; the owner must be
    trusted and locally obtained, never created from remote claim fields.
    """
    return (LOCAL if (owner is not None and bound_owner is owner and active is True
                       and type(claimed_revision) is int and
                       owner.revision==claimed_revision and
                       owner.digest==claimed_digest)
            else REMOTE)


def decide(request: ProofRequest, old_scope, new_scope):
    if type(request) is not ProofRequest or not (request.old_required or request.new_required):
        raise ValueError('explicit nonempty proof request required')
    if old_scope not in (LOCAL,REMOTE) or new_scope not in (LOCAL,REMOTE):
        raise ValueError('unrecognized source scope')
    passed = (not request.old_required or old_scope==LOCAL) and (
        not request.new_required or new_scope==LOCAL)
    return 'PROVENANCE_ADMITTED' if passed else 'PROVENANCE_UNPROVED'

if __name__=='__main__':
    owner=SourceHandle(1,'a'*64)
    old=verified_scope(owner=owner,bound_owner=owner,active=True,
                       claimed_revision=1,claimed_digest='a'*64)
    new=verified_scope(owner=owner,bound_owner=SourceHandle(1,'a'*64),active=True,
                       claimed_revision=1,claimed_digest='a'*64)
    print('old',old,'new',new,'both',decide(ProofRequest(True,True),old,new))
