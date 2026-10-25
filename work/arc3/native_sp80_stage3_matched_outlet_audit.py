"""Audit genuine original SP80 stage3 catcher neighbors from archived SDK frames.

Source-only: no simulated world, no new game execution, no inferred objective.
"""
from __future__ import annotations
import argparse, io, json, zipfile
from hashlib import sha256, blake2b
from pathlib import Path
import numpy as np

SOURCE_BASE='original-sp80-stage3-right-catcher-edge'
JSON_SHA='99a7c84a6b2d5f52e4847dbcab8510d23b5fbebcf2aa1e7e160a77b72d995273'
NPZ_SHA='5cdb6d73a16685a19132a67ed02e3781342725672bee4f6d388d3bc28e5c5542'
CASES=('catch_left3_up5','catch_left2_up5','catch_left3_up4','catch_left3_up3')
CUPS=((8,53,16,58),(26,53,34,58),(38,53,46,58),(50,53,58,58))

def require(ok,message):
    if not ok:raise ValueError('ORIGINAL_SP80_MATCHED_BOUNDARY_WALL: '+message)
def frame_hash(arr):
    return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()

def parse(word):
    out=[]
    for token in word.split():
        if token.startswith('6@'):
            x,y=map(int,token[2:].split(','))
            require(0<=x<64 and 0<=y<64,'bad native click')
            out.append((6,[x,y]))
        else:
            require(token in ('1','2','3','4','5'),'unsupported original action')
            out.append((int(token),None))
    return out

def first_changed(pre,frames,y,x):
    return next((int(i) for i,f in enumerate(frames)
                 if np.any(pre[y,x]!=f[y,x])),None)

def new6(pre,f,row):
    return np.flatnonzero((pre[row]!=6)&(f[row]==6)).astype(int).tolist()

def review(item,arr):
    case=item['original_precommitted_sdk_case']
    witness=item['real_native_entry_witness']
    actions=parse(item['actual_original_sdk_word']); n=len(actions)
    require(actions[-1]==(5,None) and sum(a==5 for a,_ in actions)==1,
            'native final action drift')
    require(item['actual_original_sdk_word'].split('6@40,42')[-1].strip().startswith('3'),
            'selected catcher movement absent')
    prefix=case+'_'+witness+'_'
    root=arr[prefix+'entry2_11'][-1]
    ledger=item['true_original_sdk_action_ledger']
    require(len(ledger)==n,'original SDK action ledger incomplete')
    previous=root
    for index,((action,xy),receipt) in enumerate(zip(actions,ledger),1):
        stack=arr[prefix+'stage3_'+str(index)]
        require(stack.ndim==3 and stack.shape[1:]==(64,64),
                'original SDK frames absent')
        after=stack[-1]
        require(receipt['original_action']==action and
                receipt['original_click_xy']==xy and
                receipt['actual_source_before_sha']==frame_hash(previous) and
                receipt['actual_source_after_sha']==frame_hash(after),
                'original native per-action receipt mismatch')
        if xy is not None:
            x,y=xy
            require(receipt['actual_source_preclick_palette']==int(previous[y,x]),
                    'source click mismatch')
        previous=after
    pre=arr[prefix+'stage3_'+str(n-1)][-1]
    frames=arr[prefix+'stage3_'+str(n)]
    first=[None]*4; maxima=[0]*4; allfour=None
    masks=[]
    for x0,y0,x1,y1 in CUPS:
        mask=pre[y0:y1+1,x0:x1+1]==11
        require(int(mask.sum())==45,'native original cup masks changed')
        masks.append(mask)
    for i,frame in enumerate(frames):
        full=0
        for j,(x0,y0,x1,y1) in enumerate(CUPS):
            pixels=int(np.count_nonzero(masks[j]&
                      (frame[y0:y1+1,x0:x1+1]==13)))
            maxima[j]=max(maxima[j],pixels)
            if pixels==45:
                full+=1
                if first[j] is None:first[j]=i
        if full==4 and allfour is None:allfour=i
    original=item['genuine_original_frame_evidence']
    bottom=first_changed(pre,frames,slice(59,63),slice(2,62))
    observed_bottom=original['first_genuine_tested_source_bottom_change']
    require(original['original_first_four_visually_full_cup_frame']==allfour and
            original['original_source_each_cup_first_full_frame']==first and
            original['original_sdk_source_frame_count']==len(frames) and
            (None if observed_bottom is None else observed_bottom['original_sdk_frame'])==bottom,
            'native source observation disagrees with original NPZ')
    selected_y,selected_x=np.nonzero(pre==9)
    onset=next((i for i,frame in enumerate(frames) if new6(pre,frame,56)),None)
    require(item['original_sdk_official_final_level']==
            ledger[-1]['official_source_level_after'],
            'original SDK level mismatch')
    return {
        'case':case,'witness':witness,
        'native_word':item['actual_original_sdk_word'],
        'official_level':item['original_sdk_official_final_level'],
        'official_state':item['original_sdk_official_final_state'],
        'root_hash':frame_hash(root),
        'pre_pour_hash':frame_hash(pre),
        'selected_catcher_bbox':[int(selected_x.min()),int(selected_y.min()),
                                 int(selected_x.max()),int(selected_y.max())],
        'returned_animation_frames':len(frames),
        'first_full_cup_frames':first,
        'maximum_cup13_pixels':maxima,
        'first_four_simultaneous':allfour,
        'first_new_palette6_y56_frame':onset,
        'first_new_palette6_y56_x':new6(pre,frames[onset],56) if onset is not None else [],
        'first_bottom_change_frame':bottom,
        'new_palette6_y56_at_bottom_change':
            new6(pre,frames[bottom],56) if bottom is not None else [],
        'last_frame_hash':frame_hash(frames[-1]),
    },(pre,frames)

def audit(path):
    with zipfile.ZipFile(path) as archive:
        j=archive.read(SOURCE_BASE+'.json')
        n=archive.read(SOURCE_BASE+'.npz')
    require(sha256(j).hexdigest()==JSON_SHA and sha256(n).hexdigest()==NPZ_SHA,
            'original archived SDK evidence digest mismatch')
    manifest=json.loads(j)
    rows=manifest['genuine_sdk_original_action_and_frame_receipts']
    require(len(rows)==manifest['genuine_original_sdk_resets']==50,
            'original native trial manifest incomplete')
    indexed={(row['original_precommitted_sdk_case'],row['real_native_entry_witness']):row
             for row in rows}
    records=[]; comparisons={}; roots=set()
    with np.load(io.BytesIO(n),allow_pickle=False) as arrays:
        for case in CASES:
            for witness in ('A','B'):
                item,_=review(indexed[(case,witness)],arrays)
                records.append(item)
                roots.add(item['root_hash'])
        for control in CASES[1:]:
            for witness in ('A','B'):
                _,s=review(indexed[(CASES[0],witness)],arrays)
                _,f=review(indexed[(control,witness)],arrays)
                left,right=s[0],f[0]
                ys,xs=np.nonzero(left!=right)
                comparison={
                    'pre_pour_differing_pixels':int(np.count_nonzero(left!=right)),
                    'pre_pour_row63_differing_pixels':
                        int(np.count_nonzero(left[63]!=right[63])),
                    'pre_pour_differing_bbox':
                        [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
                        if len(xs) else None,
                    'animation_frame_counts':[len(s[1]),len(f[1])],
                    'first_source_interior_divergence':next(
                        (i for i in range(min(len(s[1]),len(f[1])))
                         if np.any(s[1][i,:63]!=f[1][i,:63])),None),
                    'first_source_bottom_divergence':next(
                        (i for i in range(min(len(s[1]),len(f[1])))
                         if np.any(s[1][i,59:63,2:62]!=f[1][i,59:63,2:62])),None),
                }
                comparisons.setdefault(control,{})[witness]=comparison
    require(len(roots)==1,'original SDK independent stage3 entry differs')
    keyed={(row['case'],row['witness']):row for row in records}
    for case in CASES:
        a,b=keyed[(case,'A')],keyed[(case,'B')]
        require({k:v for k,v in a.items() if k!='witness'}==
                {k:v for k,v in b.items() if k!='witness'},
                'original independent native A/B witness mismatch: '+case)
    for observations in comparisons.values():
        require(observations['A']==observations['B'],
                'original source matched-frame A/B comparison mismatch')
    success=keyed[(CASES[0],'A')]
    failed=keyed[(CASES[1],'A')]
    require(success['first_four_simultaneous']==
            failed['first_four_simultaneous']==27 and
            success['official_level']==4 and failed['official_level']==3,
            'closest original four-cup success/failure distinction changed')
    return {
        'kind':'SP80_ORIGINAL_STAGE3_MATCHED_CATCHER_BOUNDARY',
        'provenance_run_id':39616395169,
        'source_artifact_id':12352298969,
        'original_source_json_sha256':JSON_SHA,
        'original_source_npz_sha256':NPZ_SHA,
        'native_source_archive_resets':50,
        'native_controls_independently_rechecked':8,
        'native_stage3_entry_hash':next(iter(roots)),
        'original_case_source_receipts':records,
        'original_success_vs_failure_frame_differences':comparisons,
        'limits':'Original archived SDK source-only comparison, not a new SDK run. Source frame index is not physical time; pixels do not decode hidden game physics or success.',
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    report=audit(args.archive)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    brief={
        'rechecked_resets':report['native_controls_independently_rechecked'],
        'case_a':{
            row['case']:{
                k:row[k] for k in (
                    'official_level','selected_catcher_bbox',
                    'first_four_simultaneous','first_new_palette6_y56_frame',
                    'first_new_palette6_y56_x','first_bottom_change_frame',
                    'new_palette6_y56_at_bottom_change')
            }
            for row in report['original_case_source_receipts']
            if row['witness']=='A'
        },
    }
    print('SP80_NATIVE_MATCHED_BOUNDARY '+json.dumps(brief,sort_keys=True),flush=True)
if __name__=='__main__':main()
