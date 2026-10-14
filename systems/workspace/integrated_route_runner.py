"""Bounded CP30 synthetic route/task fixture runner.

Executes the selected reconstructed historical source. A second invocation
against hash-checked canonical historical source is used for result comparison.
Neither Python -I nor source comparison is a security sandbox or a real-world
owner enrollment mechanism.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

# Run from the selected edition only. The same script is used to check an
# independently reassembled, manifest-hash-checked canonical edition.
_CHILD = r'''
import json, os, sys
from pathlib import Path
src=Path(sys.argv[1]).resolve(strict=True)
sys.path.insert(0,str(src))
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
from test_ab_chatbot_multi_task_dependency import MultiRouteTaskDependencyTests
from ab_chatbot_independent_process_identity import (
    issue_owner_attestations, receive_owner_attestations, new_challenge)
from finite_process_attestation import generate_fixture_keys
payload=json.load(sys.stdin)
helper=RouteBoundTaskTests('runTest')
refresh,_,left,right,_,registry,_,right_pin=helper.fixture()
chosen=left if payload['route']=='left' else right
scopes=(chosen.first.donor,chosen.first.recipient,chosen.final)
observations=lambda:tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges)) for p in scopes)
start=observations()
tasks={t['name']:helper.task(refresh,payload['route'],required_edges=[{'state':t['state'],'action':t['action']}]) for t in payload['tasks']}
secret,trust=generate_fixture_keys()
nonce=new_challenge()
issued=issue_owner_attestations(next(iter(tasks.values())),secret,nonce)
mode=payload['scenario']
if mode=='revoke-selected':
    p=chosen.first.recipient
    p.registry.revoke(p._base._tokens[0])
elif mode=='revoke-neighbor':
    if payload['route']=='left':registry.revoke(right_pin.token)
    else:
        p=left.first.recipient
        p.registry.revoke(p._base._tokens[0])
elif mode=='untrusted-key':
    trust['middle']=trust['donor']
watch=MultiRouteTaskDependencyTests.spy(helper,left,right)
result=receive_owner_attestations(issued,tasks,trust,nonce)
out={'issued_status':issued.status,'receive_status':result.status,
     'task_statuses':[[n,s] for n,s in result.tasks],
     'usable':list(result.usable),'replay_calls':result.replay_calls,
     'replay_trace':watch,'source_observations_unchanged':observations()==start,
     'proof_for_all':result.proof_for_use,
     'distinct_signer_verifier':(issued.signer_pid is not None and result.verifier_pid is not None and
      issued.signer_pid!=result.verifier_pid and os.getpid() not in (issued.signer_pid,result.verifier_pid)),
     'synthetic_fixture':True}
print(json.dumps({'payload':out,'child_pid':os.getpid()},sort_keys=True))
'''


def run_route_fixture(edition: str | Path, inputs: dict, *, timeout: int = 20) -> dict:
    folder = Path(edition)
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("CP30 edition is not an ordinary directory")
    proc = subprocess.run([sys.executable, "-I", "-c", _CHILD, str(folder)],
                          cwd=folder, input=json.dumps(inputs, sort_keys=True),
                          text=True, capture_output=True, timeout=timeout, check=False)
    if proc.returncode or len(proc.stdout) > 8192 or len(proc.stderr) > 8192:
        raise RuntimeError("CP30 synthetic route-audit child failed")
    try:
        row = json.loads(proc.stdout)
    except ValueError as exc:
        raise ValueError("CP30 child response is not JSON") from exc
    if (type(row) is not dict or set(row) != {"payload", "child_pid"} or
            type(row["child_pid"]) is not int or row["child_pid"] <= 0 or
            type(row["payload"]) is not dict):
        raise ValueError("CP30 child response shape mismatch")
    return row
