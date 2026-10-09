import numpy as np
from PIL import Image,ImageDraw
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

pal=np.array([
[0,0,0],[0,116,217],[255,65,54],[46,204,64],
[255,220,0],[170,170,170],[240,18,190],[255,133,27],
[127,219,255],[135,12,37],[0,0,0],[255,255,255],
[128,128,128],[0,128,128],[0,128,128],[255,165,0]
],dtype=np.uint8)
# override ARC-like visible colors used here
pal[9]=[135,12,37]; pal[11]=[255,255,255]; pal[14]=[0,128,128]; pal[15]=[255,165,0]

def img(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 a=a.reshape(64,64).astype(np.uint8)
 return Image.fromarray(pal[a]).resize((256,256),Image.Resampling.NEAREST)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
frames=[("start",img(env.observation_space))]
seq=[("sel9",GameAction.ACTION6,{"x":36,"y":58}),("commit9",GameAction.ACTION5,{}),
     ("sel14",GameAction.ACTION6,{"x":20,"y":58}),("commit14",GameAction.ACTION5,{}),
     ("sel11",GameAction.ACTION6,{"x":44,"y":58}),("commit11",GameAction.ACTION5,{}),
     ("sel15",GameAction.ACTION6,{"x":28,"y":58}),("commit15",GameAction.ACTION5,{})]
for name,a,data in seq:
 if a is GameAction.ACTION6:a.set_data(data)
 o=env.step(a,data=data,reasoning={"viz":name})
 frames.append((name,img(o)))
W=256*3; H=286*3
canvas=Image.new("RGB",(W,H),"white")
draw=ImageDraw.Draw(canvas)
for i,(name,im) in enumerate(frames):
 x=(i%3)*256; y=(i//3)*286
 canvas.paste(im,(x,y+20)); draw.text((x+4,y+3),name,fill="black")
canvas.save("C:/Users/teepa/arc3/solve/sb26_sequence.png")
