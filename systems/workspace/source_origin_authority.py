"""Public source-repository countersignatures over a CP30 external evidence grant.

An operator pins each public source repository's immutable GitHub identities.
Each already-enrolled source signing key must countersign the exact authority
and separate-witness publication, then publish its statement in that source
repository. This is source-side technical corroboration ONLY: GitHub write
access and a matching key do not prove legal ownership or native CP30 proof.
No source files, historical research, journals or runtime jobs are written.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .external_evidence import SCOPES, SourceEvidenceLedger, _canonical, _b64, _id
from .external_route_mapping import _parse_time, _strict_object
from .github_observation import _parse_locator, _file_at_commit
from .external_source_continuity import _verify_ancestry
from .external_authority_binding import AuthorityAnchorLedger
from .independent_authority_source import (
    IndependentWitnessLedger, _checked_public_repo, _head, _witness_file,
    verify_published_authority,
)

KIND = 'cp30-source-origin-review-authorization/v1'
STATUS = 'SOURCE_REPOSITORY_AUTHORIZATION_CORROBORATED'
_LIMIT = timedelta(minutes=5)
_REQUIRED = {'kind','scope','source_id','source_locator','source_key_sha256',
             'source_repo_id','source_owner_account_id','source_observed_commit',
             'source_observed_sha256','authority_grant_sha256','witness_id',
             'witness_publication_commit','witness_publication_sha256',
             'observation_event','native_evidence_sha256','authorization_scope',
             'issued_at','expires_at'}


def _authorization_path(scope: str) -> str:
    if scope not in SCOPES:
        raise ValueError('unrecognized source origin scope')
    return f'.well-known/cp30/source-review-{scope}.json'


class SourceOriginPolicy:
    """Receiver-pinned GitHub identity policy; operator verification remains external."""
    def __init__(self, data_dir: str | Path):
        self.path = Path(data_dir).resolve() / 'cp30_source_origin_policy.jsonl'

    def history(self) -> list[dict]:
        if not self.path.exists():
            return []
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > 160000:
            raise ValueError('unsafe source origin journal')
        events=[]; prev=None; active={}
        for number, raw in enumerate(self.path.read_text(encoding='utf-8').splitlines(), 1):
            try:
                event=json.loads(raw, object_pairs_hook=_strict_object)
            except ValueError as exc:
                raise ValueError('invalid source origin JSON history') from exc
            if (type(event) is not dict or set(event) != {'sequence','previous_hash','kind','record','event_hash'}
                or type(event['sequence']) is not int or event['sequence'] != number
                or event['previous_hash'] != prev
                or event['kind'] not in ('ORIGIN_PINNED','ORIGIN_REVOKED')
                or type(event['record']) is not dict
                or event['event_hash'] != sha256(_canonical({k:v for k,v in event.items() if k!='event_hash'})).hexdigest()):
                raise ValueError('source origin history was modified')
            row=event['record']; scope=row.get('scope')
            if scope not in SCOPES:
                raise ValueError('invalid source origin scope')
            if event['kind']=='ORIGIN_PINNED':
                if (set(row) != {'scope','source_id','locator','repo_id','owner_account_id',
                                 'key_sha256','operator','verification_reference','pinned_at'}
                    or scope in active
                    or type(row['repo_id']) is not int or row['repo_id']<=0
                    or type(row['owner_account_id']) is not int or row['owner_account_id']<=0
                    or type(row['key_sha256']) is not str or len(row['key_sha256'])!=64
                    or any(x not in '0123456789abcdef' for x in row['key_sha256'])):
                    raise ValueError('invalid or overlapping source origin pin')
                _id(row['source_id']);_id(row['operator']);_parse_locator(row['locator'])
                if type(row['verification_reference']) is not str or not 1<=len(row['verification_reference'])<=200:
                    raise ValueError('source origin needs independently checked reference')
                _parse_time(row['pinned_at']);active[scope]=row
            else:
                if (set(row) != {'scope','source_id','key_sha256','operator','revoked_at'}
                    or scope not in active
                    or active[scope]['source_id'] != row['source_id']
                    or active[scope]['key_sha256'] != row['key_sha256']):
                    raise ValueError('source origin revocation lacks active pin')
                _id(row['operator']);_parse_time(row['revoked_at']);del active[scope]
            events.append(event);prev=event['event_hash']
        return events

    def current(self) -> dict[str, dict]:
        active={}
        for entry in self.history():
            scope=entry['record']['scope']
            if entry['kind']=='ORIGIN_PINNED':active[scope]=entry['record']
            else:active.pop(scope)
        return active

    def _append(self, kind: str, record: dict) -> dict:
        events=self.history()
        item={'sequence':len(events)+1,
              'previous_hash':events[-1]['event_hash'] if events else None,
              'kind':kind,'record':record}
        item['event_hash']=sha256(_canonical(item)).hexdigest()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if self.path.is_symlink():raise ValueError('source policy symlink not allowed')
        with self.path.open('a',encoding='utf-8') as fp:
            fp.write(_canonical(item).decode('ascii')+'\n');fp.flush();os.fsync(fp.fileno())
        return record

    def pin(self,*,scope:str,source_id:str,locator:str,repo_id:int,
            owner_account_id:int,key_sha256:str,operator:str,verification_reference:str) -> dict:
        if scope not in SCOPES:raise ValueError('unknown source scope')
        _id(source_id);_id(operator);_parse_locator(locator)
        keys=SourceEvidenceLedger(self.path.parent)._state()[0]
        if (scope not in keys or keys[scope]['source_id']!=source_id
            or keys[scope]['locator']!=locator or keys[scope]['key_sha256']!=key_sha256):
            raise PermissionError('exact current source enrollment required')
        if (type(repo_id) is not int or repo_id<=0 or type(owner_account_id) is not int or owner_account_id<=0):
            raise ValueError('positive immutable GitHub IDs required')
        if type(verification_reference) is not str or not 1<=len(verification_reference)<=200:
            raise ValueError('source account and repository need an out-of-band reference')
        if scope in self.current():raise ValueError('source scope already pinned; revoke first')
        return self._append('ORIGIN_PINNED',dict(scope=scope,source_id=source_id,
            locator=locator,repo_id=repo_id,owner_account_id=owner_account_id,
            key_sha256=key_sha256,operator=operator,
            verification_reference=verification_reference,pinned_at=datetime.now(timezone.utc).isoformat()))

    def revoke(self,*,scope:str,source_id:str,key_sha256:str,operator:str)->dict:
        _id(operator)
        old=self.current().get(scope)
        if old is None or old['source_id']!=source_id or old['key_sha256']!=key_sha256:
            raise ValueError('revoke must match exact active source origin')
        return self._append('ORIGIN_REVOKED',dict(scope=scope,source_id=source_id,
            key_sha256=key_sha256,operator=operator,revoked_at=datetime.now(timezone.utc).isoformat()))


def _require_statement(statement: dict, *, scope: str, pinned: dict,
                       obs: dict, signed_grant: dict, witness: dict,
                       now: datetime) -> None:
    if type(statement) is not dict or set(statement)!=_REQUIRED or statement['kind']!=KIND:
        raise ValueError('invalid source authorization statement')
    grant=signed_grant['statement']
    expected={'scope':scope,'source_id':pinned['source_id'],
              'source_locator':pinned['locator'],'source_key_sha256':pinned['key_sha256'],
              'source_repo_id':pinned['repo_id'],'source_owner_account_id':pinned['owner_account_id'],
              'source_observed_commit':obs['commit_sha1'],
              'source_observed_sha256':obs['sha256'],
              'authority_grant_sha256':sha256(_canonical(signed_grant)).hexdigest(),
              'witness_id':witness['witness_id'],
              'witness_publication_commit':witness['publication_commit'],
              'witness_publication_sha256':witness['publication_blob_sha256'],
              'observation_event':grant['observation_event'],
              'native_evidence_sha256':grant['native_evidence_sha256'],
              'authorization_scope':'external-evidence-corroboration-only'}
    if any(statement.get(k)!=value for k,value in expected.items()):
        raise ValueError('source authorization does not bind exact observed evidence or witness')
    start=_parse_time(statement['issued_at']);end=_parse_time(statement['expires_at'])
    limit=_parse_time(grant['expires_at'])
    if (start>now+timedelta(seconds=30) or end<=now or
        not timedelta(seconds=30)<=end-start<=_LIMIT or
        start<_parse_time(grant['issued_at']) or end>limit):
        raise ValueError('source authorization is stale or outside original grant window')


def verify_source_origin_authorizations(*, data_dir: str|Path, signed_grant:dict,
        native_binding:dict, witness_id:str, confirm_grant_sha256:str,
        confirm_observation_event:str, allow_network:bool=False)->dict:
    """Read-only corroboration, including fresh separate-witness and live-native checks.

    Source *repository* publication + enrolled key consent is stronger than
    a third-party witness alone; neither establishes natural/legal identity.
    """
    if type(signed_grant) is not dict or set(signed_grant)!={'statement','signature'}:
        raise ValueError('exact signed authority grant required')
    grant=signed_grant['statement']
    digest=sha256(_canonical(signed_grant)).hexdigest()
    if (not allow_network or confirm_grant_sha256 != digest or
        confirm_observation_event!=grant.get('observation_event')):
        raise PermissionError('explicit network, grant and observation confirmations required')
    policy=SourceOriginPolicy(data_dir)
    history_before=policy.history()
    origins=policy.current()
    if set(origins)!=set(SCOPES):raise PermissionError('all three exact source origins must be operator-pinned')
    store=SourceEvidenceLedger(data_dir)
    events_before=store.history()
    keys,challenges,accepted,events=store._state()
    if grant['observation_event'] not in {r['event_hash'] for r in events if r['kind']=='SOURCE_OBSERVED'}:
        raise ValueError('source observation is not an accepted event')
    obs_event=next(e for e in events if e['event_hash']==grant['observation_event'])
    if obs_event['record']['challenge']!=grant['challenge']:
        raise ValueError('grant refers to a different source challenge')
    source_records=obs_event['record']['observations']
    for scope in SCOPES:
        row=keys.get(scope);pin=origins[scope];observed=source_records[scope]
        if row is None or any(pin[k]!=row[r] for k,r in
            [('source_id','source_id'),('locator','locator'),('key_sha256','key_sha256')]):
            raise PermissionError('source origin enrollment was revoked or changed')
        if observed['source_id']!=pin['source_id'] or observed['locator']!=pin['locator']:
            raise ValueError('source origin differs from observed source')
    witness_before=IndependentWitnessLedger(data_dir).history()
    authority_before=AuthorityAnchorLedger(data_dir).history()
    witness=verify_published_authority(data_dir=data_dir,witness_id=witness_id,
             signed_grant=signed_grant,native_binding=native_binding,
             confirm_grant_sha256=digest,allow_network=True)
    now=datetime.now(timezone.utc)
    group={};repo_cache={};heads={};authorization_deadlines=[]
    for scope in SCOPES:
        pin=origins[scope];owner,repo,branch,file_path=_parse_locator(pin['locator'])
        identity=(owner,repo)
        if identity not in repo_cache:repo_cache[identity]=_checked_public_repo(owner,repo)
        if repo_cache[identity]!={'repo_id':pin['repo_id'],'owner_account_id':pin['owner_account_id']}:
            raise ValueError('source repository identity differs from operator pin')
        headkey=(owner,repo,branch)
        if headkey not in heads:heads[headkey]=_head(owner,repo,branch)
        head=heads[headkey]
        _verify_ancestry(owner,repo,source_records[scope]['commit_sha1'],head)
        raw_file=_file_at_commit(owner,repo,file_path,head)
        if raw_file['sha256']!=source_records[scope]['sha256']:
            raise ValueError('original observed source file changed since receipt')
        publication,blob=_witness_file(owner,repo,_authorization_path(scope),head)
        _require_statement(publication['statement'],scope=scope,pinned=pin,
            obs=source_records[scope],signed_grant=signed_grant,witness=witness,now=now)
        authorization_deadlines.append(_parse_time(publication['statement']['expires_at']))
        try:
            Ed25519PublicKey.from_public_bytes(_b64(keys[scope]['public_key'],32)).verify(
                _b64(publication['signature'],64), _canonical(publication['statement']))
        except InvalidSignature as exc:
            raise ValueError('source-origin countersignature is invalid') from exc
        group[scope]={'source_id':pin['source_id'],
                      'repo_id':pin['repo_id'],'owner_account_id':pin['owner_account_id'],
                      'observed_commit':source_records[scope]['commit_sha1'],
                      'authorization_commit':head,'authorization_file_sha256':blob,
                      'authorization_path':_authorization_path(scope),
                      'authorization_url':f'https://github.com/{owner}/{repo}/blob/{head}/{_authorization_path(scope)}',
                      'observed_source_sha256':source_records[scope]['sha256'],
                      'enrolled_source_key_sha256':pin['key_sha256']}
    for (owner,repo,branch),head in heads.items():
        if _head(owner,repo,branch)!=head:
            raise ValueError('source GitHub branch moved during authorization check')
    if any(_checked_public_repo(*ident)!=info for ident,info in repo_cache.items()):
        raise ValueError('source GitHub identity changed during authorization check')
    if (datetime.now(timezone.utc)>=min([_parse_time(grant['expires_at']),*authorization_deadlines])):
        raise ValueError('source authorization expired during network verification')
    if (store.history()!=events_before or policy.history()!=history_before or
        IndependentWitnessLedger(data_dir).history()!=witness_before or
        AuthorityAnchorLedger(data_dir).history()!=authority_before):
        raise ValueError('local authority policies changed during authorization check')
    # Portable pointers to public contents; this digest is a convenient
    # comparison identifier, not a tamper-proof or externally anchored log.
    receipt={'kind':'cp30-source-origin-corroboration-receipt/v1',
             'authority_grant_sha256':digest,
             'observation_event':grant['observation_event'],
             'source_policy_tip':history_before[-1]['event_hash'] if history_before else None,
             'signed_source_evidence_tip':events_before[-1]['event_hash'] if events_before else None,
             'witness_id':witness['witness_id'],
             'witness_publication_commit':witness['publication_commit'],
             'witness_publication_sha256':witness['publication_blob_sha256'],
             'source_origin_publications':group,
             'native_cp30_task_authorized':False}
    return {'status':STATUS,'grant_sha256':digest,
            'witness_publication_commit':witness['publication_commit'],
            'source_origin_publications':group,
            'review_receipt':receipt,
            'review_receipt_sha256':sha256(_canonical(receipt)).hexdigest(),
            'enrolled_source_key_countersignatures_verified':True,
            'operator_pinned_repository_identities_checked':True,
            'independent_witness_publication_reverified':True,
            'native_snapshot_authority_reverified':True,
            'real_world_owner_identity_proved':False,
            'legal_authority_proved':False,
            'github_account_control_is_legal_authority':False,
            'external_document_claim_matches_native_full_table':False,
            'cp30_fresh_route_audit':False,'exact_task_authorized':False,
            'native_handoff_admitted':False,'new_transitions_observed':False,
            'journal_modified':False,
            'note':'Three source repositories published keyed consent over one grant and witness; technical corroboration, not identity or CP30 mathematical proof.'}
