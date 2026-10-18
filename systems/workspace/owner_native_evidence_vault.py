"""Private W13 continuation: fresh native verification, encrypted seal, restore.

Never executes a worker, uploads an artifact, publishes the journal, or grants
owner authorization. The lost original 39135756852 child journal is NOT
recoverable from its GitHub log. Future owner-approved runs can use this before
teardown, supplying an owner-held X25519 recipient key.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
from tempfile import TemporaryDirectory

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

SCHEMA="original-w13-encrypted-native-continuation/v1"
AAD=SCHEMA.encode("ascii")
PARENT="game-w13-github-001"
CHILD="game-native-verifier-github-001"
PARENT_EVENT="evt_208f2fbdb380437eb59790a9a704c0b9"
PARENT_SOURCE="798ed2399413ecbb30a1eb94c547a5517ee03dfd002600d868376f88f03f458a"
MAX_FILES=160
MAX_RAW=24*1024*1024
MAX_SEALED=40*1024*1024
SHA=re.compile("[0-9a-f]{40}\Z")
EVENT=re.compile("evt_[0-9a-f]{32}\Z")
ROOTS={"runtime.jsonl","coordinator-windows.jsonl","workstation"}


def _b64(raw: bytes)->str:
    return base64.b64encode(raw).decode("ascii")


def _unb64(value:str, *,size:int|None=None)->bytes:
    if not isinstance(value,str):
        raise ValueError("bounded key or evidence encoding required")
    try:
        raw=base64.b64decode(value,validate=True)
    except (ValueError,base64.binascii.Error) as exc:
        raise ValueError("invalid encrypted evidence encoding") from exc
    if size is not None and len(raw)!=size:
        raise ValueError("wrong cryptographic input size")
    return raw


def _path(name:str)->str:
    if not isinstance(name,str) or len(name)>250 or "\\" in name:
        raise ValueError("unsafe original native path")
    p=PurePosixPath(name)
    if (p.is_absolute() or not p.parts or ".." in p.parts or "." in p.parts
            or p.parts[0] not in ROOTS
            or (p.parts[0]!="workstation" and len(p.parts)!=1)
            or (p.parts[0]=="workstation" and len(p.parts)<2)):
        raise ValueError("native journal archive path outside bounded source")
    return str(p)


def _collect(root:Path)->list[dict]:
    for required in ("runtime.jsonl","coordinator-windows.jsonl"):
        f=root/required
        if not f.is_file() or f.is_symlink():
            raise ValueError("exact original native journals required")
    out=[]
    total=0
    for directory, dirs, files in os.walk(root,topdown=True,followlinks=False):
        rel=Path(directory).relative_to(root)
        for d in dirs:
            sub=Path(directory)/d
            if sub.is_symlink():
                raise ValueError("symlinked native source directory refused")
            if rel==Path(".") and d!="workstation":
                raise ValueError("unexpected native source directory")
        for name in files:
            f=Path(directory)/name
            if f.is_symlink() or not f.is_file():
                raise ValueError("unsafe native source file")
            filename=_path(f.relative_to(root).as_posix())
            if f.stat().st_size+total>MAX_RAW or len(out)>=MAX_FILES:
                raise ValueError("bounded private source archive exceeded")
            raw=f.read_bytes()
            total+=len(raw)
            out.append({"path":filename,"sha256":sha256(raw).hexdigest(),"data":_b64(raw)})
    if not any(x["path"].startswith("workstation/") for x in out):
        raise ValueError("native worker editions missing")
    return sorted(out,key=lambda x:x["path"])


def _witness(root:Path)->dict:
    """Use the actual original native host re-verifier, not a fixture."""
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    from .native_receipt_projection import reverify_local
    runtime=HandoffRuntime(event_store=RuntimeJournal(root/"runtime.jsonl"))
    if PARENT not in runtime.snapshot() or CHILD not in runtime.snapshot():
        raise ValueError("actual source-owned W13 parent and child required")
    if runtime.get(CHILD).dependencies!=(PARENT,):
        raise ValueError("original native verifier lost exact parent")
    original=reverify_local(root,PARENT)
    child=reverify_local(root,CHILD)
    for rec,jid,worker,version in (
        (original,PARENT,"game-worlds-w13","w13-github-v1"),
        (child,CHILD,"game-native-independent-verifier","witness-owner-v1")):
        if (rec.get("job_id")!=jid or rec.get("worker_id")!=worker
                or rec.get("worker_version")!=version
                or rec.get("recorded_status")!="COMPLETE"
                or rec.get("verification")!="FRESH_NATIVE_REVERIFICATION_LOCAL"):
            raise ValueError("original parent/child native evidence did not reverify")
    if original["source_fingerprint"]!=PARENT_SOURCE:
        raise ValueError("original owner W13 worker source changed")
    def event(r):
        results=[x for x in r["events"] if
                 x["type"]=="RESULT" and x["result_status"]=="COMPLETE"]
        if len(results)!=1 or not EVENT.fullmatch(results[0]["event_id"]):
            raise ValueError("one exact native RESULT event required")
        return results[0]["event_id"]
    if event(original)!=PARENT_EVENT:
        raise ValueError("original W13 RESULT event was replaced")
    return {"parent_event":PARENT_EVENT,"child_event":event(child),
            "parent_source_fingerprint":PARENT_SOURCE,
            "child_source_fingerprint":child["source_fingerprint"]}


def seal_verified(*,data_dir:Path,public_key_b64:str,
                  owner_execution_commit:str,output:Path)->dict:
    """Seal a REAL verified future-run journal; do not transfer or upload it."""
    root=Path(data_dir).resolve()
    out=Path(output)
    if not SHA.fullmatch(owner_execution_commit):
        raise ValueError("exact owner execution commit required")
    if out.is_symlink() or out.exists() or not out.parent.is_dir() or out.resolve().is_relative_to(root):
        raise ValueError("new explicit capsule destination outside journal required")
    recipient=X25519PublicKey.from_public_bytes(_unb64(public_key_b64,size=32))
    evidence=_witness(root)
    files=_collect(root)
    plain=json.dumps({"schema":SCHEMA,"owner_execution_commit":owner_execution_commit,
                      "witness":evidence,"files":files},
                     sort_keys=True,separators=(",",":")).encode("utf8")
    if len(plain)>MAX_SEALED:
        raise ValueError("private evidence exceeds capsule budget")
    secret=X25519PrivateKey.generate()
    public=secret.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
    salt,nonce=os.urandom(16),os.urandom(12)
    key=HKDF(algorithm=hashes.SHA256(),length=32,salt=salt,info=AAD).derive(
        secret.exchange(recipient))
    cipher=AESGCM(key).encrypt(nonce,plain,AAD)
    envelope=json.dumps({"schema":SCHEMA,"ephemeral_public":_b64(public),
                         "salt":_b64(salt),"nonce":_b64(nonce),
                         "ciphertext":_b64(cipher)},sort_keys=True,separators=(",",":")).encode()
    if len(envelope)>MAX_SEALED:
        raise ValueError("sealed capsule size exceeded")
    fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"wb") as handle:
            handle.write(envelope)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        out.unlink(missing_ok=True)
        raise
    return {"schema":SCHEMA,"sealed_sha256":sha256(envelope).hexdigest(),
            "sealed_bytes":len(envelope),"encrypted_only":True,
            "raw_journal_published":False,"owner_execution_commit":owner_execution_commit,
            "child_event":evidence["child_event"],"native_reverified_before_sealing":True}


def restore_verified(*,encrypted:Path,private_key_raw:bytes,
                     destination:Path,expected_owner_execution_commit:str,
                     expected_child_event:str)->dict:
    """Restore only exact expected original parent+child after fresh native checks."""
    if not SHA.fullmatch(expected_owner_execution_commit) or not EVENT.fullmatch(expected_child_event):
        raise ValueError("exact owner commit and native RESULT expected")
    if type(private_key_raw) is not bytes or len(private_key_raw)!=32:
        raise ValueError("owner-held raw X25519 private key required")
    src=Path(encrypted); dest=Path(destination)
    if src.is_symlink() or not src.is_file() or src.stat().st_size>MAX_SEALED:
        raise ValueError("invalid private encrypted native capsule")
    if dest.is_symlink() or dest.exists() or not dest.parent.is_dir():
        raise ValueError("restore must target new empty directory")
    envelope=json.loads(src.read_text("utf8"))
    if (type(envelope) is not dict or set(envelope)!={
        "schema","ephemeral_public","salt","nonce","ciphertext"}
            or envelope["schema"]!=SCHEMA):
        raise ValueError("foreign encrypted source capsule")
    peer=X25519PublicKey.from_public_bytes(_unb64(envelope["ephemeral_public"],size=32))
    salt=_unb64(envelope["salt"],size=16)
    nonce=_unb64(envelope["nonce"],size=12)
    cipher=_unb64(envelope["ciphertext"])
    if len(cipher)>MAX_SEALED:
        raise ValueError("unbounded private source ciphertext")
    private=X25519PrivateKey.from_private_bytes(private_key_raw)
    key=HKDF(algorithm=hashes.SHA256(),length=32,salt=salt,info=AAD).derive(private.exchange(peer))
    plain=AESGCM(key).decrypt(nonce,cipher,AAD)
    if len(plain)>MAX_SEALED:
        raise ValueError("decrypted private journal too large")
    packet=json.loads(plain)
    if (type(packet) is not dict or set(packet)!={"schema","owner_execution_commit","witness","files"}
            or packet["schema"]!=SCHEMA
            or packet["owner_execution_commit"]!=expected_owner_execution_commit
            or packet["witness"].get("parent_event")!=PARENT_EVENT
            or packet["witness"].get("child_event")!=expected_child_event):
        raise ValueError("decrypted source does not match exact owner/event")
    files=packet["files"]
    if type(files) is not list or not 3<=len(files)<=MAX_FILES:
        raise ValueError("native archive missing source files")
    if len({x.get("path") for x in files})!=len(files):
        raise ValueError("duplicate native source paths")
    with TemporaryDirectory(prefix="owner-w13-verified-",dir=dest.parent) as scratch:
        root=Path(scratch)/"native"
        root.mkdir(mode=0o700)
        total=0
        for item in files:
            if type(item) is not dict or set(item)!={"path","sha256","data"}:
                raise ValueError("unrecognized archived native entry")
            rel=_path(item["path"])
            raw=_unb64(item["data"])
            total+=len(raw)
            if total>MAX_RAW or sha256(raw).hexdigest()!=item["sha256"]:
                raise ValueError("native file SHA-256 mismatch")
            target=root/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
            target.chmod(0o600)
        fresh=_witness(root)
        if fresh!=packet["witness"] or fresh["child_event"]!=expected_child_event:
            raise ValueError("restored journal lacks exact fresh native replay")
        os.replace(root,dest)
    return {"schema":SCHEMA,"state":"RESTORED_AND_FRESH_NATIVE_REVERIFIED",
            "owner_execution_commit":expected_owner_execution_commit,
            "parent_event":PARENT_EVENT,"child_event":expected_child_event,
            "private_journal_published":False,"new_worker_executed":False}


def main(argv=None):
    p=argparse.ArgumentParser(description="Private owner W13 continuation; no job execution or upload")
    sub=p.add_subparsers(dest="operation",required=True)
    s=sub.add_parser("seal")
    s.add_argument("--data-dir",type=Path,required=True)
    s.add_argument("--public-key-file",type=Path,required=True)
    s.add_argument("--owner-execution-commit",required=True)
    s.add_argument("--output",type=Path,required=True)
    d=sub.add_parser("restore")
    d.add_argument("--sealed-file",type=Path,required=True)
    d.add_argument("--private-key-file",type=Path,required=True)
    d.add_argument("--owner-execution-commit",required=True)
    d.add_argument("--child-event",required=True)
    d.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(argv)
    if a.operation=="seal":
        if (a.public_key_file.is_symlink() or not a.public_key_file.is_file()
                or a.public_key_file.stat().st_size>128):
            raise ValueError("explicit small recipient public-key file required")
        result=seal_verified(data_dir=a.data_dir,
            public_key_b64=a.public_key_file.read_text("ascii").strip(),
            owner_execution_commit=a.owner_execution_commit,output=a.output)
    else:
        f=a.private_key_file
        if (f.is_symlink() or not f.is_file() or f.stat().st_size!=32
                or f.stat().st_mode & 0o077):
            raise ValueError("owner-held raw 0600 private key file required")
        result=restore_verified(encrypted=a.sealed_file,private_key_raw=f.read_bytes(),
            destination=a.output_dir,
            expected_owner_execution_commit=a.owner_execution_commit,
            expected_child_event=a.child_event)
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
