from __future__ import annotations
from collections import defaultdict, Counter
from itertools import product
from pathlib import Path
from PIL import Image
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def arr(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.astype(int)

def comps(a):
    h,w=a.shape; seen=np.zeros_like(a,bool); out=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(a[y,x]); q=[(y,x)]; seen[y,x]=1; pts=[]
            while q:
                cy,cx=q.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(a[ny,nx])==c:
                        seen[ny,nx]=1; q.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            out.append({'color':c,'size':len(pts),'x0':min(xs),'x1':max(xs),'y0':min(ys),'y1':max(ys)})
    return out

def ring_color(a,c):
    vals=[]
    for yy in range(c['y0']-1,c['y1']+2):
        for xx in range(c['x0']-1,c['x1']+2):
            if 0<=yy<64 and 0<=xx<64 and not (c['x0']<=xx<=c['x1'] and c['y0']<=yy<=c['y1']):
                v=int(a[yy,xx])
                if v not in (0,4):
                    vals.append(v)
    return Counter(vals).most_common(1)[0][0] if vals else None

def parse(a):
    cs=comps(a)

    target=sorted(
        [c for c in cs if c['size']==20 and c['x1']-c['x0']==5 and c['y1']-c['y0']==5 and c['y0']<=2 and c['color']!=5],
        key=lambda c:c['x0']
    )
    target_colors=[c['color'] for c in target]
    if not target_colors: return None

    literal_controls=defaultdict(list)
    for c in cs:
        if c['size']==16 and c['x1']-c['x0']==3 and c['y1']-c['y0']==3 and c['y0']>=55:
            literal_controls[c['color']].append((round((c['x0']+c['x1'])/2),round((c['y0']+c['y1'])/2)))

    call_controls=defaultdict(list)
    bottom_centers=[c for c in cs if c['color']==4 and c['size']==4 and c['x1']-c['x0']==1 and c['y1']-c['y0']==1 and c['y0']>=55]
    for c in bottom_centers:
        cc=ring_color(a,c)
        if cc is not None:
            call_controls[cc].append((round((c['x0']+c['x1'])/2),round((c['y0']+c['y1'])/2)))

    cells=[c for c in cs if c['size']==4 and c['x1']-c['x0']==1 and c['y1']-c['y0']==1 and 10<=c['y0']<=49 and c['color'] in (2,4)]
    borders=[c for c in cs if c['size']>=40 and c['color'] not in (0,2,4,5) and c['y0']>=10 and c['y1']<=50]

    groups=defaultdict(list); meta={}
    for cell in cells:
        cx=(cell['x0']+cell['x1'])/2; cy=(cell['y0']+cell['y1'])/2
        enc=[b for b in borders if b['x0']<cx<b['x1'] and b['y0']<cy<b['y1']]
        if not enc: continue
        enc.sort(key=lambda b:(b['x1']-b['x0']+1)*(b['y1']-b['y0']+1))
        parent=enc[0]; pc=parent['color']; meta[pc]=parent
        if cell['color']==2:
            token=('slot',(round(cx),round(cy)))
        else:
            cc=ring_color(a,cell)
            if cc is None: continue
            token=('call',cc)
        groups[pc].append((cell['x0'],token))

    # Detect fixed 4x4 literal blocks inside each function panel.
    # They can be connected to a same-color border and therefore disappear
    # as separate connected components (as in the level-4 blue literal).
    for pc,parent in list(meta.items()):
        existing=groups.get(pc,[])
        if not existing:
            continue
        row_centers=[]
        for _,tok in existing:
            if tok[0]=='slot':
                row_centers.append(tok[1][1])
        # fixed-call cells are aligned with the body too; recover their y from cells
        enclosed_cells=[]
        for cell in cells:
            cx=(cell['x0']+cell['x1'])/2; cy=(cell['y0']+cell['y1'])/2
            if parent['x0']<cx<parent['x1'] and parent['y0']<cy<parent['y1']:
                enclosed_cells.append(cy)
        row_centers.extend(enclosed_cells)
        if not row_centers:
            continue
        body_y=sum(row_centers)/len(row_centers)
        candidates=[]
        for yy in range(parent['y0']+2, parent['y1']-2):
            for xx in range(parent['x0']+2, parent['x1']-2):
                block=a[yy:yy+4,xx:xx+4]
                if block.shape!=(4,4):
                    continue
                v=int(block[0,0])
                if v in (0,2,4,5) or not np.all(block==v):
                    continue
                cy=yy+1.5
                if abs(cy-body_y)>1.1:
                    continue
                candidates.append((xx,yy,v))
        # Collapse overlapping detections of the same visual token.
        kept=[]
        for xx,yy,v in sorted(candidates):
            if any(abs(xx-kx)<=3 and abs(yy-ky)<=3 for kx,ky,_ in kept):
                continue
            kept.append((xx,yy,v))
        for xx,yy,v in kept:
            groups[pc].append((xx,('literal',v)))

    funcs={c:[tok for _,tok in sorted(items)] for c,items in groups.items()}
    if not funcs: return None
    root=min(funcs,key=lambda c:meta[c]['y0'])
    slots=[]
    for fc,items in funcs.items():
        for kind,val in items:
            if kind=='slot' and val not in slots:
                slots.append(val)
    return {
        'target':target_colors,'literals':literal_controls,'calls':call_controls,
        'funcs':funcs,'root':root,'slots':slots
    }

def solve_spec(spec):
    target=spec['target']; funcs=spec['funcs']; root=spec['root']
    limits={('lit',c):len(ps) for c,ps in spec['literals'].items()}
    limits.update({('call',c):len(ps) for c,ps in spec['calls'].items()})
    choices=[('lit',c) for c in spec['literals']] + [('call',c) for c in spec['calls'] if c in funcs]
    if not choices:
        return None

    def match_choice(choice,pos,assign,used,stack):
        if pos>len(target):
            return []
        kind,color=choice
        if kind=='lit':
            if pos<len(target) and target[pos]==color:
                return [(pos+1,assign,used)]
            return []
        return match_func(color,pos,assign,used,stack)

    def match_tokens(fc,index,pos,assign,used,stack):
        if pos>len(target):
            return []
        items=funcs[fc]
        if index>=len(items):
            return [(pos,assign,used)]
        kind,val=items[index]
        states=[]
        if kind=='literal':
            if pos<len(target) and target[pos]==val:
                states=[(pos+1,assign,used)]
        elif kind=='call':
            states=match_func(val,pos,assign,used,stack+(fc,))
        else:
            slot=val
            if slot in assign:
                states=match_choice(assign[slot],pos,assign,used,stack+(fc,))
            else:
                for choice in choices:
                    if used.get(choice,0)>=limits.get(choice,0):
                        continue
                    # Literal choices can be rejected without recursion.
                    if choice[0]=='lit' and (pos>=len(target) or target[pos]!=choice[1]):
                        continue
                    a2=dict(assign); a2[slot]=choice
                    u2=dict(used); u2[choice]=u2.get(choice,0)+1
                    states.extend(match_choice(choice,pos,a2,u2,stack+(fc,)))
        out=[]
        for p2,a2,u2 in states:
            out.extend(match_tokens(fc,index+1,p2,a2,u2,stack))
        return out

    def match_func(fc,pos,assign,used,stack):
        if fc not in funcs or fc in stack:
            return []
        return match_tokens(fc,0,pos,assign,used,stack)

    for pos,assign,used in match_func(root,0,{}, {}, ()):
        if pos==len(target):
            return assign
    return None

def click(e,p):
    x,y=p
    a=GameAction.ACTION6; a.set_data({'x':int(x),'y':int(y)})
    return e.step(a,data=a.action_data.model_dump(),reasoning={})

arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
e=arcade.make('sb26')
PALETTE=np.array([[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],[127,219,255],[135,12,37],[255,255,255],[102,102,102],[177,13,201],[255,128,191],[18,163,255],[61,153,112]],dtype=np.uint8)
Path(r'C:\Users\teepa\arc3\frames').mkdir(exist_ok=True)
for level in range(8):
    raw=arr(e.observation_space)
    Image.fromarray(PALETTE[raw]).resize((512,512),Image.Resampling.NEAREST).save(fr'C:\Users\teepa\arc3\frames\sb26_csp_level{level+1}.png')
    spec=parse(raw)
    print('\nLEVEL',level+1,'SPEC',spec)
    if spec is None: break
    assign=solve_spec(spec)
    print('ASSIGN',assign)
    if assign is None: break
    pools={
        'lit':{c:list(ps) for c,ps in spec['literals'].items()},
        'call':{c:list(ps) for c,ps in spec['calls'].items()},
    }
    for slot,choice in assign.items():
        kind,color=choice
        ctrl=pools[kind][color].pop(0)
        click(e,ctrl); click(e,slot)
    out=e.step(GameAction.ACTION5,data={},reasoning={})
    print('RESULT',out.levels_completed,out.state)
    if out.state.name=='WIN': break
