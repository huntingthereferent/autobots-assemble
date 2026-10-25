"""Read-only reproducible audit of archived *original* SP80 SDK frame stacks.

Inputs are official GitHub Actions ZIP artifacts containing preserved .npz
arrays from genuine Arcade(OperationMode.NORMAL) calls. This is not a
surrogate ARC game, solver, or model of private engine mechanics.

Claim tested: for each stage4 original returned ACTION5 stack, the
first root-top border source-palette1 -> source-palette14 frame occurs
one frame after the first NEW palette6 in source y5..7,x5..58
relative to the actual original pre-action frame.

A success in prior level3 is not evidence that source cell x23..25
newly arrived: it was already palette6 before the native winning pour.
Source-occupancy correlation is separate from original SDK level>=5.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
from pathlib import Path
from collections import Counter
import numpy as np

RE_STAGE4=re.compile(r"^(.*)_(A|B)_stage4_(\d+)$")

def load_npz(path:Path):
    if path.suffix==".zip":
        with zipfile.ZipFile(path) as z:
            files=[n for n in z.namelist() if n.endswith(".npz")]
            if len(files)!=1:raise ValueError("Expected one authentic SDK NPZ in "+str(path))
            return np.load(io.BytesIO(z.read(files[0])),allow_pickle=False)
    return np.load(path,allow_pickle=False)

def first_frame(frames,predicate):
    return next((int(t) for t,frame in enumerate(frames) if predicate(frame)),None)

def inspect_archive(filename:Path):
    a=load_npz(filename)
    rows=[]
    for key in a.files:
        match=RE_STAGE4.match(key)
        if not match:continue
        stack=a[key]
        if stack.ndim!=3 or stack.shape[1:]!=(64,64) or len(stack)<20:
            continue
        case,witness,number=match.group(1),match.group(2),int(match.group(3))
        prior=(f"{case}_{witness}_stage4_{number-1}" if number>1
               else f"{case}_{witness}_entry3_34")
        rootname=f"{case}_{witness}_entry3_34"
        if prior not in a.files or rootname not in a.files:
            raise AssertionError("Missing original pre-action/root source: "+key)
        pre=a[prior][-1];root=a[rootname][-1]
        if pre.shape!=(64,64) or root.shape!=(64,64):
            raise AssertionError("Original source before-pour/root shape changed")
        newsource_mask=pre[5:8,5:59]!=6
        topborder_mask=root[2:5,5:62]==1
        if not newsource_mask.any() or not topborder_mask.any():
            raise AssertionError("Original source preconditions absent")
        first_new=first_frame(stack,lambda frame:
            np.any(newsource_mask&(frame[5:8,5:59]==6)))
        first_flash=first_frame(stack,lambda frame:
            np.any(topborder_mask&(frame[2:5,5:62]==14)))
        uid=hashlib.blake2b(
            pre.tobytes()+stack.tobytes(),digest_size=16).hexdigest()
        rows.append({
            "array_key":key,
            "full_original_sdk_frame_count":len(stack),
            "first_new_top_strip_palette6_frame":first_new,
            "first_original_top_border_palette14_frame":first_flash,
            "first_flash_exactly_next_frame":first_new is not None and
                                               first_flash==first_new+1,
            "native_pre_and_pour_source_blake2b16":uid
        })
    return rows

def successful_reference(filename:Path):
    a=load_npz(filename)
    pre="catch_left3_up5_A_stage3_33"
    pour="catch_left3_up5_A_stage3_34"
    if pre not in a.files or pour not in a.files:
        raise AssertionError("Verified stage3 source-winning witness missing")
    before=a[pre][-1][5:8,23:26]
    first=a[pour][0][5:8,23:26]
    if before.shape!=(3,3) or first.shape!=(3,3):
        raise AssertionError("Source observation array not full native 3px cell")
    return {
        "reference_original_stage3_winner":pour,
        "y5_7_x23_25_palette6_pixels_before_original_action5":int((before==6).sum()),
        "y5_7_x23_25_palette6_pixels_first_original_returned_frame":int((first==6).sum()),
        "already_present_before_source_win":bool(np.all(before==6)),
        "scope":"Reference cell is existing palette6, NOT newly arriving win mechanism."
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archives",nargs="+",required=True,type=Path)
    parser.add_argument("--stage3-success-archive",type=Path)
    parser.add_argument("--out",type=Path)
    opts=parser.parse_args()
    allrows=[];provenance=[]
    for filename in opts.archives:
        rows=inspect_archive(filename)
        if not rows:raise AssertionError("No original 64x64 SDK stage4 pours in "+str(filename))
        provenance.append({
            "original_artifact_basename":filename.name,
            "source_pour_stack_count":len(rows),
            "source_relation_matches":sum(int(r["first_flash_exactly_next_frame"]) for r in rows)})
        allrows+=rows
    failed=[r for r in allrows if not r["first_flash_exactly_next_frame"]]
    unique={r["native_pre_and_pour_source_blake2b16"] for r in allrows}
    summary={
        "kind":"READ_ONLY_ORIGINAL_SP80_STAGE4_TOP_SOURCE_ARRIVAL_BORDER_TIMING",
        "genuine_original_sdk_source_pour_stacks_checked":len(allrows),
        "distinct_original_prepour_and_full_frame_stack_digests":len(unique),
        "observed_plus_one_timing_matches":len(allrows)-len(failed),
        "falsifying_original_source_frame_stacks":failed,
        "archive_provenance":provenance,
        "winning_stage3_preexisting_source_reference":
            successful_reference(opts.stage3_success_archive)
            if opts.stage3_success_archive else None,
        "epistemic_boundary":"Observed original SDK source-frame timing only; distinct artifacts may repeat runs and witnesses. Does not establish a private engine cause or a Level5 win. Preserve F3-48 mathematics separately."
    }
    body=json.dumps(summary,indent=2,sort_keys=True)+"\n"
    if opts.out:
        opts.out.parent.mkdir(parents=True,exist_ok=True)
        opts.out.write_text(body)
    print("SP80_ORIGINAL_TOP_BORDER_REPLAY "+json.dumps({
        k:v for k,v in summary.items() if k!="archive_provenance"
    },sort_keys=True),flush=True)
    if failed:
        raise AssertionError("Found original native SDK counterexamples; inspect saved read-only report")

if __name__=="__main__":main()
