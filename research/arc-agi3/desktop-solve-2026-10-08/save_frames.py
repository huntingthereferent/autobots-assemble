import numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
for gid in ["sb26","ls20"]:
    env=arc.make(gid)
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3: a=a[-1]
    a=a.reshape(64,64).astype(np.uint8)
    # ARC palette, RGB
    pal=np.array([
        [0,0,0],[0,116,217],[255,65,54],[46,204,64],
        [255,220,0],[170,170,170],[240,18,190],[255,133,27],
        [127,219,255],[135,12,37],[0,0,0],[255,255,255],
        [128,128,128],[128,0,128],[0,128,128],[255,165,0]
    ],dtype=np.uint8)
    rgb=pal[a]
    out = "C:/Users/teepa/arc3/solve/" + gid + "_initial.png"
    Image.fromarray(rgb).resize((512,512),Image.Resampling.NEAREST).save(out)
