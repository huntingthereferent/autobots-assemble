import numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from program_schema import induce_program,_frame_candidates,_clusters_inside
from latent import perceive,grid,effect

PAL=np.array([
[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],
[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[128,0,128],[0,128,128],[255,165,0]
],dtype=np.uint8)

def step(env,aname,data=None,label=""):
    a=getattr(GameAction,aname)
    if a is GameAction.ACTION6:
        x,y=data
        a.set_data({"x":int(x),"y":int(y)})
        return env.step(a,data={"x":int(x),"y":int(y)},reasoning={"probe":label})
    return env.step(a,data={},reasoning={"probe":label})

def advance_to_l3():
    env=arc.make("sb26")
    for _ in range(3):
        meta=induce_program(env.observation_space)
        assert meta, ("parser failed before L3",env.observation_space.levels_completed)
        for aname,data in meta["plan"]:
            step(env,aname,data,"advance_generic")
    assert env.observation_space.levels_completed==3
    return env

def save(obs,name):
    a=grid(obs).astype(np.uint8)
    Image.fromarray(PAL[a]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/"+name+".png")

def level3_roles(obs):
    g=grid(obs); s=perceive(obs)
    frames=[r for r in _frame_candidates(obs) if 8<=r[2] and r[4]<=52]
    # Real routine frames: prefer non-background-like frame colors and outermost per geometry.
    # Main is upper routine containing the largest number of red tiny slots.
    infos=[]
    for r in frames:
        cls=_clusters_inside(g,r)
        terminals=[c for c in cls if c["color"]==2 and c["size"]<=16]
        infos.append((len(terminals),r,terminals,cls))
    infos.sort(key=lambda z:(-z[0],z[1][2],-(z[1][3]-z[1][1])))
    main=infos[0]
    main_slots=sorted([(c["cx"],c["cy"]) for c in main[2]],key=lambda p:(p[1],p[0]))
    # Lower routine color is the non-main real frame color whose interior includes same-color marker + terminals.
    lower=None
    for n,r,terms,cls in infos[1:]:
        same=[c for c in cls if c["color"]==r[0] and c["size"]>=9]
        if terms and same:
            lower=(r,terms,same); break
    assert lower, infos
    routine_color=lower[0][0]

    # Bottom palette tokens are compact components below separator. Find token matching routine color.
    bottom=[o for o in s.objects if o.y0>=54 and o.x1-o.x0+1<=7 and o.y1-o.y0+1<=7 and o.size>=8]
    routine_tokens=[o for o in bottom if o.color==routine_color]
    assert routine_tokens, (routine_color,bottom)
    calltok=max(routine_tokens,key=lambda o:(o.x1-o.x0+1)*(o.y1-o.y0+1))
    call_xy=(calltok.center2[0]//2,calltok.center2[1]//2)
    call_solid = calltok.size == (calltok.x1-calltok.x0+1)*(calltok.y1-calltok.y0+1)

    # Ordinary literal: choose a solid bottom token with different color.
    literals=[o for o in bottom if o.color!=routine_color and o.size==(o.x1-o.x0+1)*(o.y1-o.y0+1)]
    literals.sort(key=lambda o:o.center2[0])
    lit=literals[0]
    lit_xy=(lit.center2[0]//2,lit.center2[1]//2)
    return {
      "main_rect":main[1],"main_slots":main_slots,
      "routine_color":routine_color,"call_xy":call_xy,"call_solid":call_solid,
      "literal_color":lit.color,"literal_xy":lit_xy,
    }

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)

for mode in ("call","literal"):
    env=advance_to_l3()
    before=env.observation_space
    roles=level3_roles(before)
    slot=roles["main_slots"][2]
    pick=roles["call_xy"] if mode=="call" else roles["literal_xy"]
    print("ROLES",mode,roles,"chosen_slot",slot,"pick",pick)
    step(env,"ACTION6",pick,"select_"+mode)
    selected=env.observation_space
    step(env,"ACTION6",slot,"write_"+mode)
    after=env.observation_space
    e=effect(selected,after)
    print("WRITE_EFFECT",mode,e)
    g=grid(after)
    x,y=slot
    print("PATCH",mode)
    for yy in range(max(0,y-3),min(64,y+4)):
        print(yy, g[yy,max(0,x-4):min(64,x+5)].tolist())
    save(before,"sb26_l3_before_"+mode)
    save(selected,"sb26_l3_selected_"+mode)
    save(after,"sb26_l3_written_"+mode)
