from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4804)
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
p5=(3,1,3,3,4,4,4,2,1,4,4,1,4,2,3,3,3,2,2,3,2,4,4,4,4,3,1,4,4,3,2,4,1,3,3,3,3,1,3,3,3,4,1,4,4,4,4,4,1,4,2,3,3,3,3,3,3,2,4,4,2,4,4,4,4)
prefix=p1+p2+p3+p4+p5
P6=(4,4,2,4,6,2,2,4,4,2,1,4,2,3,1,3,2,6,4,4,4,3,3,3,3,2,2,4,1,3,1,4,6,2,2,2)
P7=(4,1,4,4,2,4,6,4,2,2,2,2,2,2,1,1,6,1,6,1,3,6,4,4,3,3,3,2,4,4,6,2,6,2,6,2,2,6,3,3,3,3,2,4,4,1,1,1,4,4,4)
P8=(4,4,6,2,2,4,2,3,2,2,2,1,1,1,6,4,4,4,4,3,2,3,3,1)
import sys,logging,hashlib,numpy as np
from pathlib import Path
starter=Path('C:/Users/teepa/arc3/ARC-AGI-3-Kaggle-Starter')
sys.path.insert(0,str(starter))
sys.path.insert(0,str(starter/'vendor/ARC-AGI-3-Agents'))
from agents.agent import Agent
from arcengine import GameState
full=prefix+P6+P7+P8
maker=Arcade(operation_mode=OperationMode.NORMAL)
build=maker.make('sk48')
script=[]
for z in full:
 data={}
 if z==6:
  gg=build._game;other=next(k for k in gg.xpmcmtbcv if k!=gg.vzvypfsnt)
  data={'x':int(other.x+2),'y':int(other.y+2)}
 script.append((z,data))
 r=build.step(GameAction.from_id(z),data=data)
assert r.state.name=='WIN' and r.levels_completed==8
class RecordedPolicy(Agent):
 MAX_ACTIONS=300
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.ix=0
 def is_done(self,frames,latest_frame):
  return latest_frame.state is GameState.WIN or self.ix>=len(script)
 def choose_action(self,frames,latest_frame):
  z,data=script[self.ix];self.ix+=1
  action=GameAction.from_id(z)
  if data:action.set_data(data)
  return action
second=Arcade(operation_mode=OperationMode.NORMAL)
env=second.make('sk48')
agent=RecordedPolicy(card_id='scratch-compare',game_id='sk48',agent_name='SK48-portable-scratch',ROOT_URL='http://localhost',record=False,arc_env=env,tags=['scratch'])
logging.disable(logging.CRITICAL)
agent.main()
print('AGENT_INTERFACE','state',agent.frames[-1].state.name,'levels',agent.frames[-1].levels_completed,'actions',agent.ix,'score',second.get_scorecard().score,'clicks',sum(z==6 for z,d in script),'no_internal_game_access_during_agent_run',True,flush=True)
print('CHECKPOINTS',[(i+1,agent.frames[i+1].levels_completed) for i in (13,43,76,103,168,204,255,279)],flush=True)
