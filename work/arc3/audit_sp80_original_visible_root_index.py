"""Read-only rooted A/B visible-state and action-index audit for original SP80.

For every authentic SDK .npz archive with stage4_N 64x64 returns,
compare full-frame hashes against native Stage4 action indices.
No native or synthetic game runs here: raw saved source output only.

An observed full frame hash can collide at adjacent action indices.
Ask whether it also appears at two DIFFERENT indices of the SAME parity.
No such collision was observed in the October 25 11,054-frame audit,
which is an empirical sample-bound result, not a native transition law.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import blake2b,sha256
import io,json,re,zipfile
from pathlib import Path
import numpy as np

RE_KEY=re.compile(r"^(.*)_([AB])_stage4_(\d+)$")

def inspect_archive(path:Path):
    with zipfile.ZipFile(path) as z:
        entries=[n for n in z.namelist() if n.endswith(".npz")]
        if len(entries)!=1:
            raise ValueError("Expected one original SDK .npz evidence array: "+str(path))
        content=z.read(entries[0])
    rows=[]
    with np.load(io.BytesIO(content),allow_pickle=False) as arr:
        for key in arr.files:
            m=RE_KEY.match(key)
            if not m:continue
            frames=arr[key]
            if frames.ndim!=3 or frames.shape[1:]!=(64,64) or len(frames)<1:
                raise AssertionError("Non-native or empty SP80 frame array "+key)
            after=frames[-1]
            digest=blake2b(np.ascontiguousarray(after).tobytes(),digest_size=16).hexdigest()
            rows.append({
                "original_evidence_array":key,
                "stage4_action_index":int(m.group(3)),
                "last_original_frame_blake2b16":digest,
                "returned_original_frame_count":int(len(frames)),
            })
    if not rows:
        raise AssertionError("Source archive contains no original stage4 frame returns: "+str(path))
    return rows,sha256(content).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archives",nargs="+",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    index=defaultdict(set)
    source=[];total=0
    for file in args.archives:
        rows,source_digest=inspect_archive(file)
        total+=len(rows)
        for r in rows:
            index[r["last_original_frame_blake2b16"]].add(r["stage4_action_index"])
        source.append({"original_sdk_archive":file.name,
                       "source_npz_sha256":source_digest,
                       "original_stage4_action_return_count":len(rows)})
    same_parity_different_index=[]
    adjacent_index=[]
    for root,indices in index.items():
        seq=sorted(indices)
        for i,a in enumerate(seq):
            for b in seq[i+1:]:
                if (b-a)%2==0:
                    same_parity_different_index.append({
                        "original_visible_root":root,
                        "action_indices":[a,b]})
                elif b==a+1:
                    adjacent_index.append({
                        "original_visible_root":root,
                        "action_indices":[a,b]})
    report={
        "kind":"READ_ONLY_ORIGINAL_SP80_VISIBLE_ROOT_STAGE4_INDEX_AUDIT",
        "original_archives":source,
        "recorded_genuine_original_stage4_action_return_arrays":total,
        "distinct_original_full_visible_frame_hashes":len(index),
        "source_images_at_adjacent_action_indices":len(adjacent_index),
        "distinct_visible_root_even_action_index_distance_pairs":
            same_parity_different_index,
        "number_of_equal_parity_different_index_pairs":
            len(same_parity_different_index),
        "limit":"No original hidden-state or global parity rule follows. Many arrays are repeated original witnesses and programs. Official native level5/WIN remains the progression condition."
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2)+"\n")
    print("SP80_ORIGINAL_VISIBLE_INDEX_AUDIT "+json.dumps({
        k:v for k,v in report.items() if k!="original_archives"},sort_keys=True))

if __name__=="__main__":
    main()
