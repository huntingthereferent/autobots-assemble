from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
BOOT=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
e=a.make('ar25');r=None
for z in BOOT:r=e.step(GameAction.from_id(z),data={})
def st(label):
 g=e._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 print(label,"LC",r.levels_completed,"LEV",g.level_index,"SEL",sel,"POS",[(s.x,s.y) for s in g.ayyvxqrhnzw],"HUJ",g.hujpxmlafgh,flush=True)
st("START")
seq=[1]*7+[5]+[4]*7+[2]*7+[5]+[3]*12+[2]*5
for i,z in enumerate(seq,1):
 r=e.step(GameAction.from_id(z),data={})
 st(f"{i}:{z}")
 if r.state.name!="NOT_FINISHED" or r.levels_completed>2:
  print("STOP",r.state.name,r.levels_completed,flush=True);break
