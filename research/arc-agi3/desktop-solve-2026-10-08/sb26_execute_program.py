import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
pal={14:(20,58),15:(28,58),9:(36,58),11:(44,58)}
slots=[(22,29),(28,29),(34,29),(40,29)]
target=[9,14,11,15]
obs=env.observation_space
for color,slot in zip(target,slots):
 x,y=pal[color]
 a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
 obs=env.step(a,data={"x":x,"y":y},reasoning={"h":"select"})
 b=GameAction.ACTION6;b.set_data({"x":slot[0],"y":slot[1]})
 obs=env.step(b,data={"x":slot[0],"y":slot[1]},reasoning={"h":"write"})
print("program written",obs.levels_completed,obs.state)
for i in range(1,21):
 a=GameAction.ACTION5
 obs=env.step(a,data={},reasoning={"h":"execute","i":i})
 print("step",i,"levels",obs.levels_completed,"win_levels",obs.win_levels,"state",obs.state)
 if obs.levels_completed>0 or "GAME_OVER" in str(obs.state) or "WIN" in str(obs.state):
  break
