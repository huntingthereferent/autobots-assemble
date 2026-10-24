"""Independent reconciliation of four preserved original ARC4 SDK evidence ZIPs.

Rehashes bytes, actual 64x64 NPZ stacks, original source per-action ledgers,
all four cup first-fill times, native official status, and workstation journals.
Does NOT run/approximate the game or claim external trusted attestation.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import blake2b, sha256
import io
import json
from pathlib import Path
import zipfile
import numpy as np

FROZEN = (
    ("arc4-468-corrected.zip","arc4-direct-upper-right1-contrast",14,
     "dfab8262d56a74ebd5aae7bbc39c194b7380a0cfb604c3b414029e48d63d8250",
     "72468b7d61ac902cd6d9eada6930c6a8054879a0749715f49d73bd45e8dd713c"),
    ("arc4-519.zip","original-upper-history",16,
     "640a423ed9305ad28aa8b67c44b666cba7b7fbac1820fb56a89138b97058b107",
     "2b22ae084c9246c0be9adaf73999ab815fe6f2dade15931b8c725771fc0d2fa5"),
    ("arc4-520.zip","original-row63-followup",16,
     "ba4ebbf71879d5735dae8c592709ac513627ee17e863a978455c6ae58959a0ba",
     "62a01182cf2247feb3dfde2ed24960a56dd87abe58f9e11fb9dcf0ab53ab18a5"),
    ("arc4-521.zip","original-right-middle-transfer",16,
     "5947d0d8ddabda46d0486b112f6965aa311be8fa8157111b1ea8e2254b233a51",
     "2baeea795ac3baeaaa06a95b68a2dcd0c4d2694c91a0c04df87bbe5c3f81f9b9"),
)
CUPS={"lateral":(5,35,10,43),"top_left":(17,5,25,10),
      "top_middle":(35,5,43,10),"top_right":(47,5,55,10)}

def require(ok,message):
    if not ok:raise ValueError("ORIGINAL_ARC4_AUDIT_WALL: "+message)

def sha(data):return sha256(data).hexdigest()
def framehash(a):return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()
def command(token):
    if token.startswith("6@"):
        x,y=map(int,token[2:].split(","))
        require(0<=x<64 and 0<=y<64,"out-of-bounds original SDK click")
        return 6,[x,y]
    require(token in {"1","2","3","4","5"},"unsupported original action token")
    return int(token),None

def cups(root,stack):
    first={name:None for name in CUPS}
    maximum={name:0 for name in CUPS}
    simultaneous=None
    for name,(x0,y0,x1,y1) in CUPS.items():
        require(int(np.count_nonzero(root[y0:y1+1,x0:x1+1]==11))==45,
                "original cup root mask changed")
    for t,frame in enumerate(stack):
        count=0
        for name,(x0,y0,x1,y1) in CUPS.items():
            original=(root[y0:y1+1,x0:x1+1]==11)
            filled=int(np.count_nonzero(original&(frame[y0:y1+1,x0:x1+1]==13)))
            maximum[name]=max(maximum[name],filled)
            if filled==45:
                count+=1
                if first[name] is None:first[name]=t
        if count==4 and simultaneous is None:simultaneous=t
    return first,maximum,simultaneous

def audit(path,base,budget,expected_json,expected_npz):
    require(path.exists(),"original GitHub Actions archive unavailable: "+path.name)
    with zipfile.ZipFile(path) as zipped:
        json_bytes=zipped.read(base+".json")
        npz_bytes=zipped.read(base+".npz")
        require(sha(json_bytes)==expected_json and sha(npz_bytes)==expected_npz,
                "archived native source byte digest mismatch")
        source=json.loads(json_bytes)
        workstation=json.loads(zipped.read("workstation/arc4-workstation-return.json"))
        require(workstation["json_sha256"]==sha(json_bytes) and
                workstation["npz_sha256"]==sha(npz_bytes) and
                workstation["native_resets"]==budget and workstation["state"]=="PARTIAL",
                "workstation hashes/decision do not match source artifact")
        trials=source["native_cases"]
        require(len(trials)==budget==source["original_sdk_resets"],
                "native original reset ledger count mismatch")
        require(source["official_level5_or_WIN_count"]==0 and
                source["official_level_histogram"]=={"4":budget},
                "original SDK reports a different official level boundary")
        original_roots=set(); witnessed=set(); cup_histogram=Counter()
        verified_actions=0
        with np.load(io.BytesIO(npz_bytes),allow_pickle=False) as stacks:
            for item in trials:
                case=item.get("case",item.get("control"))
                witness=item.get("witness",item.get("native_witness"))
                require(witness in ("A","B") and (case,witness) not in witnessed,
                        "native independent witness absent or duplicated")
                witnessed.add((case,witness))
                script=item.get("original_source_word",item.get("original_word",
                              item.get("source_action_word")))
                actions=[command(token) for token in script.split()]
                require(actions[-1]==(5,None) and sum(a==5 for a,_ in actions)==1,
                        "original stage4 action words changed")
                ledger=item.get("native_action_receipts",item.get(
                    "genuine_stage4_action_ledger",item.get("genuine_stage4_action_receipts")))
                require(len(actions)==len(ledger),"native SDK per-step ledger incomplete")
                prefix=case+"_"+witness+"_"
                root=stacks[prefix+"entry3_34"][-1]
                require(root.shape==(64,64),"authentic original stage4 64x64 entry missing")
                original_roots.add(framehash(root))
                before=root
                for index,((native_action,xy),entry) in enumerate(zip(actions,ledger),1):
                    frames=stacks[prefix+"stage4_"+str(index)]
                    require(frames.ndim==3 and frames.shape[1:]==(64,64),
                            "missing original SDK returned animation")
                    after=frames[-1]
                    require(entry["genuine_original_action"]==native_action and
                            entry["real_native_click_xy"]==xy and
                            entry["original_sdk_frame_stack_count"]==len(frames),
                            "native SDK command/return receipt disagrees with frames")
                    require(entry["source_frame_before_blake2b16"]==framehash(before)
                            and entry["source_frame_after_blake2b16"]==framehash(after),
                            "per-action original source frame hash disagrees with NPZ")
                    if xy is not None:
                        x,y=xy
                        require(entry["original_source_pixel_before_click"]==int(before[y,x]),
                                "original native SDK click pixel mismatch")
                    require(entry["original_sdk_level_before"]==4,
                            "source native state left original level4 unexpectedly")
                    before=after
                    verified_actions+=1
                official=item.get("official_level",item.get("sdk_level"))
                state=item.get("official_state",item.get("sdk_state"))
                flag=item.get("official_level5_or_WIN")
                require(official==ledger[-1]["original_sdk_level_after"]==4 and
                        state==ledger[-1]["original_sdk_state_after"]=="NOT_FINISHED"
                        and flag is False,
                        "original native official game level/state contradicted by source ledger")
                animation=stacks[prefix+"stage4_"+str(len(actions))]
                first,maximum,simultaneous=cups(root,animation)
                observations=item.get("source_observation",item.get("source"))
                if "source_cups" in observations:
                    observations=observations["source_cups"]
                recorded_first=observations.get("first_full_cup_frames",
                                               observations.get("source_first_full_cups"))
                recorded_max=observations.get("maximum_original_cup13_pixels",
                                             observations.get("source_max_filled_cups"))
                recorded_four=observations.get("first_four_simultaneous_frame",
                                              observations.get("source_first_four_simultaneous"))
                require(recorded_first==first and recorded_max==maximum
                        and recorded_four==simultaneous,
                        "native source cup timing/maximum differs from original NPZ")
                cup_histogram[sum(v==45 for v in maximum.values())]+=1
        require(len(original_roots)==1,"original SDK stage4 source roots differ")
        cases={name for name,_ in witnessed}
        require(len(witnessed)==budget and
                all({w for n,w in witnessed if n==name}=={"A","B"} for name in cases),
                "original independent A/B witness pair missing")
        journal=zipped.read("workstation/runtime.jsonl").decode("utf8")
        lane=zipped.read("workstation/workspace.jsonl").decode("utf8")
        require(workstation["job"] in journal and
                workstation["workspace_lane"] in lane and
                expected_json in lane and expected_npz in lane,
                "workstation journal provenance/sha witness absent")
        selected=[p for p in zipped.namelist()
                  if p.startswith("workstation/selected/") and p.endswith(".py")]
        edition=[p for p in zipped.namelist()
                 if p.startswith("workstation/workstation/") and p.endswith(".py")]
        require(len(selected)==len(edition)==1 and
                zipped.read(selected[0])==zipped.read(edition[0]),
                "executed native source differs from private workstation edition")
        return {"archive":path.name,"native_resets":budget,
                "source_action_receipts_rehashed":verified_actions,
                "original_stage4_root_blake2b16":next(iter(original_roots)),
                "official_level4":budget,"official_level5_or_WIN":0,
                "visual_cups_filled_histogram":dict(sorted(cup_histogram.items())),
                "job":workstation["job"],
                "source_json_sha256":expected_json,"source_npz_sha256":expected_npz}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    results=[audit(args.directory/name,base,n,js,npz)
             for name,base,n,js,npz in FROZEN]
    roots={r["original_stage4_root_blake2b16"] for r in results}
    require(len(roots)==1,"cross-run authentic original SDK root mismatch")
    report={"kind":"ORIGINAL_ARC4_INDEPENDENT_CROSS_ARCHIVE_AUDIT",
            "archives_reconciled":len(results),
            "native_resets":sum(r["native_resets"] for r in results),
            "native_action_receipts_rehashed":sum(r["source_action_receipts_rehashed"]
                                                 for r in results),
            "original_stage4_root_blake2b16":next(iter(roots)),
            "verified_official_level5_or_WIN":0,
            "evidence":results,
            "boundary":"Reconciliation of existing genuine-source archives; no fresh game resets, source authentication external to the archive, or inference about private engine/physics."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print("ARC4_CROSS_ARCHIVE_VERIFIED "+json.dumps(report,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
