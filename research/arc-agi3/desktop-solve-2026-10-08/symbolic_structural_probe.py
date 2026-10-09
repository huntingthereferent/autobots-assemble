from __future__ import annotations
from collections import defaultdict, Counter
from pathlib import Path
from PIL import Image
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def frame_arr(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.astype(int)

def comps(a):
    h,w=a.shape
    seen=np.zeros_like(a,bool); out=[]
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

def parse(a):
    cs=comps(a)
    target=[c for c in cs if c['size']==20 and c['x1']-c['x0']==5 and c['y1']-c['y0']==5 and c['y0']<=2 and c['color']!=5]
    target=sorted(target,key=lambda c:c['x0'])
    target_colors=[c['color'] for c in target]
    palette=[c for c in cs if c['size']==16 and c['x1']-c['x0']==3 and c['y1']-c['y0']==3 and c['y0']>=55 and c['color'] in set(target_colors)]
    pal={c['color']:(round((c['x0']+c['x1'])/2),round((c['y0']+c['y1'])/2)) for c in palette}

    cells=[c for c in cs if c['size']==4 and c['x1']-c['x0']==1 and c['y1']-c['y0']==1 and 10<=c['y0']<=49 and c['color'] in (2,4)]
    borders=[c for c in cs if c['size']>=40 and c['color'] not in (0,2,4,5) and c['y0']>=10 and c['y1']<=50]

    groups=defaultdict(list); meta={}
    for cell in cells:
        cx=(cell['x0']+cell['x1'])/2; cy=(cell['y0']+cell['y1'])/2
        enclosing=[b for b in borders if b['x0']<cx<b['x1'] and b['y0']<cy<b['y1']]
        if not enclosing: continue
        enclosing.sort(key=lambda b:(b['x1']-b['x0']+1)*(b['y1']-b['y0']+1))
        parent=enclosing[0]
        pc=parent['color']; meta[pc]=parent
        if cell['color']==2:
            token=('slot',(round(cx),round(cy)))
        else:
            # yellow 2x2 center inside a colored 4x4 call token
            ring=[]
            for yy in range(cell['y0']-1,cell['y1']+2):
                for xx in range(cell['x0']-1,cell['x1']+2):
                    if 0<=yy<64 and 0<=xx<64 and not (cell['x0']<=xx<=cell['x1'] and cell['y0']<=yy<=cell['y1']):
                        v=int(a[yy,xx])
                        if v not in (0,4):
                            ring.append(v)
            if not ring: continue
            call_color=Counter(ring).most_common(1)[0][0]
            token=('call',call_color)
        groups[pc].append((cell['x0'],token))

    funcs={c:[tok for _,tok in sorted(items)] for c,items in groups.items()}
    if not funcs: return None
    root=min(funcs, key=lambda c:meta[c]['y0'])

    def expand(c,stack=()):
        if c in stack or c not in funcs: raise ValueError(('bad call',c,stack,funcs))
        out=[]
        for kind,val in funcs[c]:
            if kind=='slot': out.append(val)
            else: out.extend(expand(val,stack+(c,)))
        return out
    flat=expand(root)
    if len(flat)!=len(target_colors):
        return {'error':'length','target':target_colors,'root':root,'funcs':funcs,'flat':flat,'palette':pal}
    assign={}
    for slot,color in zip(flat,target_colors):
        if slot in assign and assign[slot]!=color:
            return {'error':'constraint','target':target_colors,'root':root,'funcs':funcs,'flat':flat,'assign':assign}
        assign[slot]=color
    if any(c not in pal for c in assign.values()):
        return {'error':'palette','target':target_colors,'assign':assign,'palette':pal}
    return {'target':target_colors,'root':root,'funcs':funcs,'flat':flat,'assign':assign,'palette':pal}

def click(e,x,y):
    act=GameAction.ACTION6; act.set_data({'x':int(x),'y':int(y)})
    return e.step(act,data=act.action_data.model_dump(),reasoning={})

arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
e=arcade.make('sb26')
PALETTE=np.array([[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],[127,219,255],[135,12,37],[255,255,255],[102,102,102],[177,13,201],[255,128,191],[18,163,255],[61,153,112]],dtype=np.uint8)
Path(r'C:\Users\teepa\arc3\frames').mkdir(exist_ok=True)
for level in range(8):
    obs=e.observation_space
    raw=frame_arr(obs)
    Image.fromarray(PALETTE[raw]).resize((512,512),Image.Resampling.NEAREST).save(fr'C:\Users\teepa\arc3\frames\sb26_auto_level{level+1}.png')
    p=parse(raw)
    print('LEVEL',level+1,'PARSE',p)
    if not p or 'error' in p: break
    for slot,color in p['assign'].items():
        click(e,*p['palette'][color]); click(e,*slot)
    out=e.step(GameAction.ACTION5,data={},reasoning={})
    print('RESULT',out.levels_completed,out.state)
    if out.state.name=='WIN': break
