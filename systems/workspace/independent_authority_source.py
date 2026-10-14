"""External, independently *published* attestation of a CP30 authority grant.

A separately configured public GitHub repository publishes an Ed25519-signed
statement covering the exact, locally verified, source/native authority grant.
Independence here is only separate GitHub account ID, repo ID, and verifier
key; none establishes organizational independence, legal title or CP30 proof.
Explicit network authorization, no new transition observations, no runtime.
"""
from __future__ import annotations

import base64
import binascii
from datetime import datetime, timedelta, timezone
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import re
from typing import Any, Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .external_evidence import _canonical, SourceEvidenceLedger, SCOPES
from .external_route_mapping import _parse_time, _strict_object
from .external_authority_binding import (
    AuthorityAnchorLedger, _key, _signature, verify_authority_binding,
)
from .github_observation import _github_json, _parse_locator, _GIT_SHA

KIND = "cp30-independent-authority-publication/v1"
_STATUS = "SEPARATE_GITHUB_WITNESS_PUBLICATION_VERIFIED"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}\Z")
_REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\Z")
_PATH = re.compile(r"[A-Za-z0-9._/-]{1,256}\Z")
_FIELDS = {"kind", "witness_id", "authority_id", "authority_key_sha256",
           "grant_sha256", "observation_event", "native_evidence_sha256",
           "native_process_identity_sha256", "review_reference", "review_method",
           "issued_at", "expires_at"}
_WINDOW = timedelta(minutes=5)
_MAX_FILE = 12_000


def _safe_id(v: Any) -> str:
    if type(v) is not str or not _ID.fullmatch(v):
        raise ValueError("unsafe witness identifier")
    return v


def _nonneg_id(v: Any) -> int:
    if type(v) is not int or v <= 0:
        raise ValueError("immutable GitHub identity ID required")
    return v


def _identity(*, owner: str, repo: str, branch: str, path: str) -> None:
    if (not all(type(v) is str for v in (owner,repo,branch,path))
            or not _NAME.fullmatch(owner) or not _REPO.fullmatch(repo)
            or not _ID.fullmatch(branch) or branch in ('.','..')
            or not _PATH.fullmatch(path)
            or any(part in ('','.','..') for part in path.split('/'))):
        raise ValueError("unsafe witness GitHub locator")


def _checked_public_repo(owner: str, repo: str) -> dict:
    info = _github_json(f"/repos/{owner}/{repo}")
    account = info.get("owner")
    if (type(account) is not dict or info.get("full_name") != f"{owner}/{repo}"
            or info.get("private") is not False
            or type(info.get("id")) is not int or info["id"] <= 0
            or type(account.get("id")) is not int or account["id"] <= 0
            or account.get("login") != owner):
        raise ValueError("independent witness repository identity unverified")
    return {"repo_id":info["id"],"owner_account_id":account["id"]}


def _head(owner: str, repo: str, branch: str) -> str:
    item = _github_json(f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
    obj = item.get("object")
    sha = obj.get("sha") if type(obj) is dict else None
    if (type(sha) is not str or not _GIT_SHA.fullmatch(sha)
            or obj.get('type') != 'commit'):
        raise ValueError("witness GitHub branch head invalid")
    return sha


def _witness_file(owner: str,repo: str, path: str,commit: str) -> tuple[dict,str]:
    item = _github_json(f"/repos/{owner}/{repo}/contents/{path}?ref={commit}")
    if (item.get("type") != "file" or item.get("path") != path
            or item.get("encoding") != "base64" or type(item.get("content")) is not str
            or type(item.get("size")) is not int or item["size"] > _MAX_FILE
            or len(item["content"]) > 20000):
        raise ValueError("invalid public witness file response")
    try:
        blob = base64.b64decode(item["content"].replace('\n',''),validate=True)
    except (ValueError,binascii.Error) as exc:
        raise ValueError("invalid witness file encoding") from exc
    git_sha = sha1(f"blob {len(blob)}\0".encode()+blob).hexdigest()
    if (len(blob)!=item["size"] or len(blob)>_MAX_FILE or item.get("sha")!=git_sha):
        raise ValueError("witness Git blob content mismatch")
    try:
        payload = json.loads(blob,object_pairs_hook=_strict_object)
    except (ValueError,UnicodeDecodeError) as exc:
        raise ValueError("public witness publication has invalid JSON") from exc
    if type(payload) is not dict or set(payload)!={"statement","signature"}:
        raise ValueError("signed witness publication must contain exact fields")
    return payload,sha256(blob).hexdigest()


class IndependentWitnessLedger:
    """Local pinned policy for second publication source, not global trust."""
    def __init__(self,data_dir: str|Path):
        self.path=Path(data_dir).resolve()/"cp30_independent_witnesses.jsonl"

    def history(self) -> list[dict]:
        if not self.path.exists():return []
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size>200_000:
            raise ValueError("unsafe witness policy journal")
        result=[]; prev=None; active={}
        for idx,line in enumerate(self.path.read_text(encoding='utf-8').splitlines(),1):
            try: item=json.loads(line,object_pairs_hook=_strict_object)
            except ValueError as exc:raise ValueError("invalid witness journal JSON") from exc
            if (type(item) is not dict or set(item)!={"sequence","previous_hash","kind","record","event_hash"}
                or type(item["sequence"]) is not int or item["sequence"]!=idx
                or item["previous_hash"]!=prev or item["kind"] not in ('WITNESS_PINNED','WITNESS_REVOKED')
                or type(item["record"]) is not dict
                or item["event_hash"]!=sha256(_canonical({k:v for k,v in item.items() if k!='event_hash'})).hexdigest()):
                raise ValueError("invalid witness policy chain")
            r=item["record"]
            if item["kind"]=='WITNESS_PINNED':
                if set(r)!={"witness_id","owner","repo","branch","path","repo_id","owner_account_id",
                            "public_key","fingerprint","operator","verification_reference","pinned_at"}:
                    raise ValueError("invalid witness pin record")
                _safe_id(r['witness_id']);_safe_id(r['operator'])
                _identity(owner=r['owner'],repo=r['repo'],branch=r['branch'],path=r['path'])
                _nonneg_id(r['repo_id']);_nonneg_id(r['owner_account_id'])
                if (sha256(_key(r['public_key'])).hexdigest()!=r['fingerprint']
                    or r['witness_id'] in active or type(r['verification_reference']) is not str
                    or not 1<=len(r['verification_reference'])<=200):
                    raise ValueError("invalid or overlapping witness pin")
                _parse_time(r['pinned_at']);active[r['witness_id']]=r
            else:
                if set(r)!={"witness_id","fingerprint","operator","revoked_at"}:
                    raise ValueError("invalid witness revocation record")
                _safe_id(r['witness_id']);_safe_id(r['operator']);_parse_time(r['revoked_at'])
                if (r['witness_id'] not in active or active[r['witness_id']]['fingerprint']!=r['fingerprint']):
                    raise ValueError("witness revocation lacks exact active pin")
                del active[r['witness_id']]
            result.append(item);prev=item['event_hash']
        return result

    def current(self)->dict[str,dict]:
        active={}
        for e in self.history():
            r=e['record']
            if e['kind']=='WITNESS_PINNED':active[r['witness_id']]=r
            else:active.pop(r['witness_id'])
        return active

    def _append(self,kind:str,record:dict)->dict:
        entries=self.history()
        entry={'sequence':len(entries)+1,'previous_hash':entries[-1]['event_hash'] if entries else None,
               'kind':kind,'record':record}
        entry['event_hash']=sha256(_canonical(entry)).hexdigest()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if self.path.is_symlink():raise ValueError('unsafe witness journal symlink')
        with self.path.open('a',encoding='utf-8') as f:
            f.write(_canonical(entry).decode('ascii')+'\n');f.flush();os.fsync(f.fileno())
        return entry

    def pin(self,*,witness_id:str,owner:str,repo:str,branch:str,path:str,repo_id:int,
            owner_account_id:int,public_key:str,confirm_fingerprint:str,operator:str,
            verification_reference:str)->dict:
        _safe_id(witness_id);_safe_id(operator)
        _identity(owner=owner,repo=repo,branch=branch,path=path)
        _nonneg_id(repo_id);_nonneg_id(owner_account_id)
        if sha256(_key(public_key)).hexdigest()!=confirm_fingerprint:
            raise PermissionError("witness fingerprint needs exact independent confirmation")
        if type(verification_reference) is not str or not 1<=len(verification_reference)<=200:
            raise ValueError("witness enrollment requires out-of-band verification reference")
        if witness_id in self.current():raise ValueError("active witness must be revoked before rotation")
        return self._append('WITNESS_PINNED',{
            'witness_id':witness_id,'owner':owner,'repo':repo,'branch':branch,'path':path,
            'repo_id':repo_id,'owner_account_id':owner_account_id,'public_key':public_key,
            'fingerprint':confirm_fingerprint,'operator':operator,
            'verification_reference':verification_reference,'pinned_at':datetime.now(timezone.utc).isoformat()
        })['record']

    def revoke(self,*,witness_id:str,confirm_fingerprint:str,operator:str)->dict:
        _safe_id(witness_id);_safe_id(operator)
        current=self.current().get(witness_id)
        if current is None or current['fingerprint']!=confirm_fingerprint:
            raise ValueError('witness revocation needs exact active key')
        return self._append('WITNESS_REVOKED',{
            'witness_id':witness_id,'fingerprint':confirm_fingerprint,'operator':operator,
            'revoked_at':datetime.now(timezone.utc).isoformat()})['record']


def _valid_statement(statement:dict,*,witness_id:str,grant:dict)->None:
    if type(statement) is not dict or set(statement)!=_FIELDS or statement['kind']!=KIND:
        raise ValueError('invalid independent publication statement fields')
    if statement['witness_id']!=witness_id:
        raise ValueError('wrong independent witness identity')
    original=grant['statement']
    equal={'authority_id':original['authority_id'],
           'authority_key_sha256':original['authority_key_sha256'],
           'grant_sha256':sha256(_canonical(grant)).hexdigest(),
           'observation_event':original['observation_event'],
           'native_evidence_sha256':original['native_evidence_sha256'],
           'native_process_identity_sha256':original['native_process_identity_sha256']}
    if any(statement.get(k)!=v for k,v in equal.items()):
        raise ValueError('publication does not bind exact authority grant and native evidence')
    if type(statement.get('review_method')) is not str or statement['review_method'] not in ('independent-document-review','out-of-band-owner-contact'):
        raise ValueError('unsupported independent witness review method')
    if type(statement.get('review_reference')) is not str or not 1<=len(statement['review_reference'])<=200:
        raise ValueError('independent witness must name review evidence reference')
    start=_parse_time(statement['issued_at']);end=_parse_time(statement['expires_at'])
    now=datetime.now(timezone.utc)
    if start>now+timedelta(seconds=30) or end<=now or not timedelta(seconds=30)<=end-start<=_WINDOW:
        raise ValueError('witness publication expired or issued in future')
    grant_from=_parse_time(original['issued_at']);grant_end=_parse_time(original['expires_at'])
    if start<grant_from or end>grant_end:
        raise ValueError('witness publication not valid within original authority grant')


def verify_published_authority(*,data_dir:str|Path,witness_id:str,signed_grant:dict,
                               native_binding:dict,allow_network:bool=False,
                               confirm_grant_sha256:str)->dict:
    """Explicit GET of separately controlled publication, plus live native replay.

    `native_binding` contains parameters to the existing exact live-native
    verifier, never a caller-defined callback which could return invented proof.
    The returned status is separate-publication corroboration, NOT real-world
    authority. No journal writes or CP30 work admissions occur.
    """
    if type(signed_grant) is not dict or set(signed_grant)!={'statement','signature'}:
        raise ValueError('exact previously signed authority grant required')
    digest=sha256(_canonical(signed_grant)).hexdigest()
    if not allow_network or confirm_grant_sha256!=digest:
        raise PermissionError('explicit network permission and exact grant digest required')
    _safe_id(witness_id)
    pinned=IndependentWitnessLedger(data_dir)
    policy_before=pinned.history()
    source_before=SourceEvidenceLedger(data_dir).history()
    authority_before=AuthorityAnchorLedger(data_dir).history()
    row=pinned.current().get(witness_id)
    if row is None:raise PermissionError('independent public witness not enrolled')
    statement=signed_grant['statement']
    if type(statement) is not dict or 'authority_id' not in statement:
        raise ValueError('invalid underlying authority grant')
    authority_active=AuthorityAnchorLedger(data_dir).current().get(statement['authority_id'])
    if authority_active is None or authority_active['fingerprint']!=statement.get('authority_key_sha256'):
        raise PermissionError('original authority anchor is no longer current')
    source_active=SourceEvidenceLedger(data_dir)._state()[0]
    source_accounts=set()
    for scope in SCOPES:
        entry=source_active.get(scope)
        if entry is None:raise ValueError('missing enrolled signed source scope')
        owner,repo,branch,path=_parse_locator(entry['locator'])
        source_accounts.add((owner,repo))
    if type(native_binding) is not dict or set(native_binding)!={'challenge','observation_event','source_files',
                                     'native_source_root','source_capture','authority_id',
                                     'authority_public_key','anchor_fingerprint'}:
        raise ValueError('exact native authority verification parameters required')
    if (native_binding['authority_id']!=statement['authority_id']
        or native_binding['challenge']!=statement['challenge']
        or native_binding['observation_event']!=statement['observation_event']):
        raise ValueError('native verification parameters differ from signed grant')
    if (row['fingerprint']==authority_active['fingerprint']
        or row['fingerprint'] in {entry['key_sha256'] for entry in source_active.values()}):
        raise ValueError('witness key is not independent of authority and source keys')
    if (row['owner'],row['repo']) in source_accounts or row['owner'] in {o for o,r in source_accounts}:
        raise ValueError('witness GitHub account must differ from enrolled source accounts')
    # Fetch identity and branch before the publication, and both again after
    # verification to catch common source changes. This is NOT a global lock.
    identity=_checked_public_repo(row['owner'],row['repo'])
    if identity!={'repo_id':row['repo_id'],'owner_account_id':row['owner_account_id']}:
        raise ValueError('independent publisher changed its GitHub repository identity')
    # GitHub login spelling alone is not account independence. Verify the
    # provider's immutable owner ID for every declared source repository.
    sources_before={p:_checked_public_repo(*p) for p in sorted(source_accounts)}
    if any(info['owner_account_id']==identity['owner_account_id']
           for info in sources_before.values()):
        raise ValueError('witness and source have the same GitHub account ID')
    commit=_head(row['owner'],row['repo'],row['branch'])
    doc,blob=_witness_file(row['owner'],row['repo'],row['path'],commit)
    _valid_statement(doc['statement'],witness_id=witness_id,grant=signed_grant)
    raw=_key(row['public_key'])
    try:Ed25519PublicKey.from_public_bytes(raw).verify(_signature(doc['signature']),_canonical(doc['statement']))
    except InvalidSignature as exc:raise ValueError('external witness signature unproved') from exc
    result=verify_authority_binding(data_dir=data_dir,signed_grant=signed_grant,**native_binding)
    if type(result) is not dict or result.get('status')!='OPERATOR_ANCHORED_SNAPSHOT_DELEGATION_VERIFIED':
        raise ValueError('live native authority grant has not been reverified')
    if any(result.get(k)!=v for k,v in {'native_evidence_sha256':statement['native_evidence_sha256'],
                                      'observation_event':statement['observation_event'],
                                      'native_handoff_admitted':False,'exact_task_authorized':False}.items()):
        raise ValueError('native authority recheck does not match publication')
    if (any(_checked_public_repo(*p)!=info for p,info in sources_before.items())
        or _checked_public_repo(row['owner'],row['repo'])!=identity
        or _head(row['owner'],row['repo'],row['branch'])!=commit
        or pinned.history()!=policy_before
        or SourceEvidenceLedger(data_dir).history()!=source_before
        or AuthorityAnchorLedger(data_dir).history()!=authority_before
        or pinned.current().get(witness_id)!=row):
        raise ValueError('independent publisher or receiver policy changed during verification')
    return {'status':_STATUS,'witness_id':witness_id,'witness_key_sha256':row['fingerprint'],
            'witness_repo_id':row['repo_id'],'witness_owner_account_id':row['owner_account_id'],
            'publication_commit':commit,'publication_blob_sha256':blob,
            'authority_grant_sha256':digest,'exact_signed_grant_revalidated':True,
            'live_native_snapshot_revalidated':True,'separate_published_repository_verified':True,
            'separate_witness_key_verified':True,
            'independent_organization_authenticated':False,'legal_ownership_proved':False,
            'real_world_identity_proved':False,'cp30_fresh_route_audit':False,
            'exact_cp30_task_authorized':False,'native_handoff_admitted':False,
            'journal_modified':False,
            'note':'External witness publication and current local native grant match; repository/account separation does not prove independent controller or legitimate authority.'}
