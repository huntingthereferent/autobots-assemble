"""Generic visible program-schema induction.

Recognizes a family where colored rectangular routines contain terminal slots and
calls to other routines by matching frame colors. A target sequence and palette
define terminal values. No game IDs or fixed coordinates.
"""
from __future__ import annotations
from collections import Counter,defaultdict,deque
import numpy as np
from latent import grid,perceive

def _bg(g):
    vals,cnts=np.unique(g,return_counts=True)
    return int(vals[int(np.argmax(cnts))])

def _coverage(vals,color):
    if len(vals)==0:return 0.0
    return float(np.count_nonzero(vals==color))/len(vals)

def _frame_candidates(frame):
    g=grid(frame); bg=_bg(g)
    H,W=g.shape
    colors=[int(c) for c in np.unique(g) if int(c)!=bg]
    rects=[]

    # A. component-bbox rectangles, tolerant of call connectors overwriting border.
    s=perceive(frame)
    for o in s.objects:
        w=o.x1-o.x0+1; h=o.y1-o.y0+1
        if w<12 or h<7: continue
        c=o.color
        top=g[o.y0,o.x0:o.x1+1]
        bot=g[o.y1,o.x0:o.x1+1]
        left=g[o.y0:o.y1+1,o.x0]
        right=g[o.y0:o.y1+1,o.x1]
        cov=min(_coverage(top,c),_coverage(bot,c),_coverage(left,c),_coverage(right,c))
        if cov>=0.55:
            rects.append((c,o.x0,o.y0,o.x1,o.y1,cov,"bbox"))

    # B. pair long horizontal runs of same color; useful when a call/stem is
    # connected to the routine frame and expands the component bbox.
    for c in colors:
        runs=[]
        for y in range(H):
            x=0
            while x<W:
                if int(g[y,x])!=c:
                    x+=1;continue
                x0=x
                while x<W and int(g[y,x])==c:x+=1
                x1=x-1
                if x1-x0+1>=12:runs.append((y,x0,x1))
        by_span=defaultdict(list)
        for y,x0,x1 in runs:by_span[(x0,x1)].append(y)
        for (x0,x1),ys in by_span.items():
            ys=sorted(ys)
            for i,y0 in enumerate(ys):
                for y1 in ys[i+1:]:
                    h=y1-y0+1
                    if h<7:continue
                    left=g[y0:y1+1,x0];right=g[y0:y1+1,x1]
                    cov=min(_coverage(left,c),_coverage(right,c))
                    if cov>=0.65:
                        rects.append((c,x0,y0,x1,y1,cov,"runs"))

    # Dedupe near-identical rectangles; prefer tighter/high-coverage.
    uniq=[]
    for r in sorted(rects,key=lambda r:((r[3]-r[1]+1)*(r[4]-r[2]+1),-r[5])):
        c,x0,y0,x1,y1,cv,src=r
        duplicate=False
        for q in uniq:
            if c==q[0] and max(abs(x0-q[1]),abs(y0-q[2]),abs(x1-q[3]),abs(y1-q[4]))<=1:
                duplicate=True;break
        if not duplicate:uniq.append(r)
    return uniq

def _clusters_inside(g,rect):
    c,x0,y0,x1,y1,_,_=rect
    bg=_bg(g)
    yy0,yy1=y0+1,y1-1;xx0,xx1=x0+1,x1-1
    sub=g[yy0:yy1+1,xx0:xx1+1]
    h,w=sub.shape
    seen=np.zeros((h,w),dtype=bool)
    out=[]
    for sy in range(h):
        for sx in range(w):
            if seen[sy,sx]:continue
            col=int(sub[sy,sx])
            stack=[(sy,sx)];seen[sy,sx]=True;pts=[]
            while stack:
                cy,cx=stack.pop();pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(sub[ny,nx])==col:
                        seen[ny,nx]=True;stack.append((ny,nx))
            if col==bg:continue
            xs=[xx0+p[1] for p in pts];ys=[yy0+p[0] for p in pts]
            out.append({"color":col,"size":len(pts),"x0":min(xs),"x1":max(xs),"y0":min(ys),"y1":max(ys),
                        "cx":round(sum(xs)/len(xs)),"cy":round(sum(ys)/len(ys))})
    return out

def induce_program(frame):
    g=grid(frame);bg=_bg(g)
    frames=_frame_candidates(frame)
    if not frames:return None

    # Prefer work-area frames below the target row and above palette row.
    frames=[r for r in frames if r[2]>=8 and r[4]<=52]
    if not frames:return None
    frame_colors={r[0] for r in frames}

    routines={}
    invoked=set()
    terminal_colors=Counter()
    for r in frames:
        elems=[]
        for cl in _clusters_inside(g,r):
            col=cl["color"]
            if col in frame_colors and col!=r[0]:
                elems.append(("call",col,(cl["cx"],cl["cy"]),cl))
                invoked.add(col)
            elif cl["size"]<=16:
                # Candidate terminal. Repeated tiny same-color blocks are strongest.
                elems.append(("terminal",col,(cl["cx"],cl["cy"]),cl))
                terminal_colors[col]+=1
        # keep only compact sequence-like elements
        elems.sort(key=lambda e:(e[2][0],e[2][1]))
        routines[r[0]]={"rect":r,"elements":elems}

    if not routines:return None
    # Choose repeated terminal color globally; calls use frame colors and are excluded.
    candidates=[(n,c) for c,n in terminal_colors.items() if c not in frame_colors]
    if not candidates:return None
    _,terminal_color=max(candidates)

    for rc,info in routines.items():
        info["elements"]=[
            e for e in info["elements"]
            if e[0]=="call" or (e[0]=="terminal" and e[1]==terminal_color)
        ]

    roots=[c for c in routines if c not in invoked]
    if not roots:return None
    # Main is the uppermost uncalled routine with meaningful elements.
    roots=[c for c in roots if routines[c]["elements"]]
    if not roots:return None
    root=min(roots,key=lambda c:routines[c]["rect"][2])

    flat=[]
    stack=set()
    def expand(c):
        if c in stack or c not in routines:return False
        stack.add(c)
        for typ,col,coord,cl in routines[c]["elements"]:
            if typ=="terminal":
                flat.append(coord)
            else:
                if not expand(col):
                    stack.remove(c);return False
        stack.remove(c);return True
    if not expand(root) or not flat:return None

    # Palette: bottom solid equal-size squares with distinct colors.
    s=perceive(frame)
    palette_candidates=[]
    groups=defaultdict(list)
    for o in s.objects:
        w=o.x1-o.x0+1;h=o.y1-o.y0+1
        if o.y0<54 or o.size!=w*h or w<3 or h<3 or w>6 or h>6:continue
        groups[(o.size,w,h)].append(o)
    for _,row in groups.items():
        row=sorted(row,key=lambda o:o.center2[0])
        if len(row)>=3 and len({o.color for o in row})==len(row):
            palette_candidates.append(row)
    if not palette_candidates:return None
    palette=max(palette_candidates,key=len)
    palette_by_color={o.color:(o.center2[0]//2,o.center2[1]//2) for o in palette}

    # Target sequence: one top exemplar per palette color, sorted left-to-right.
    refs=[]
    for color in palette_by_color:
        opts=[o for o in s.objects if o.color==color and o.y1<=8 and o.size>=16]
        if not opts:return None
        opts.sort(key=lambda o:(o.center2[1],-o.size))
        refs.append(opts[0])
    refs=sorted(refs,key=lambda o:o.center2[0])
    target=[o.color for o in refs]

    if len(target)!=len(flat):
        return None

    plan=[]
    for color,slot in zip(target,flat):
        if color not in palette_by_color:return None
        plan.append(("ACTION6",palette_by_color[color]))
        plan.append(("ACTION6",slot))
    plan.append(("ACTION5",None))
    return {
        "schema":"recursive_reference_program",
        "frames":[(c,info["rect"],[(e[0],e[1],e[2]) for e in info["elements"]]) for c,info in routines.items()],
        "root":root,
        "terminal_color":terminal_color,
        "flat_slots":flat,
        "target":target,
        "palette":palette_by_color,
        "plan":plan,
    }