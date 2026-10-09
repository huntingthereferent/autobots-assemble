from arc_agi import Arcade,OperationMode
from arcengine import GameAction,GameState
import json,hashlib,sys,pathlib,logging
import numpy as np
folder=pathlib.Path(r'C:\Users\teepa\arc3\AB_ARC_EVIDENCE')
data=json.loads((folder/'ft09_verified_6of6.json').read_text(encoding='utf-8'))
steps=[tuple(p) for lv in data['paths'] for p in lv]
def sign(o):return hashlib.sha256(np.asarray(o.frame[-1],dtype=np.int16).tobytes()).hexdigest()[:20]
for trial in range(2):
 arc=Arcade(operation_mode=OperationMode.NORMAL);e=arc.make('ft09');prev=0;milestones=[]
 for i,(x,y) in enumerate(steps,1):
  r=e.step(GameAction.ACTION6,data={'x':x,'y':y})
  if r.levels_completed>prev:prev=r.levels_completed;milestones.append((i,prev))
  if r.state is GameState.WIN:break
 print('FRESH_REPLAY',trial,'MILESTONES',milestones,'ACTIONS',i,'STATE',r.state.name,'SCORE',arc.get_scorecard().score,'PASS',r.state is GameState.WIN and milestones==[(z,i+1) for i,z in enumerate(data['milestones'])],flush=True)
sys.path.insert(0,r'C:\Users\teepa\arc3\ARC-AGI-3-Kaggle-Starter\vendor\ARC-AGI-3-Agents')
from agents.agent import Agent
arc=Arcade(operation_mode=OperationMode.NORMAL);env=arc.make('ft09');lookup={};conflicts=[]
for k,(x,y) in enumerate(steps):
 o=env.observation_space;sig=(o.levels_completed,sign(o));a=(x,y)
 if sig in lookup and lookup[sig]!=a:conflicts.append(k)
 lookup[sig]=a
 env.step(GameAction.ACTION6,data={'x':x,'y':y})
print('LOOKUP','STATE_COUNT',len(lookup),'CONFLICTS',conflicts,flush=True)
class FramePolicy(Agent):
 MAX_ACTIONS=100
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.matched=0;self.unknown=0
 def is_done(self,frames,latest_frame):return latest_frame.state is GameState.WIN or self.unknown>0
 def choose_action(self,frames,latest_frame):
  p=lookup.get((latest_frame.levels_completed,sign(latest_frame)))
  if p is None:self.unknown+=1;return GameAction.ACTION5
  self.matched+=1;act=GameAction.ACTION6;act.set_data({'x':p[0],'y':p[1]});return act
logging.disable(logging.CRITICAL)
fresh_arc=Arcade(operation_mode=OperationMode.NORMAL);fresh=fresh_arc.make('ft09')
policy=FramePolicy(card_id='scratch',game_id='ft09',agent_name='ft09-visual-proof',ROOT_URL='http://localhost',record=False,arc_env=fresh)
policy.main()
print('AGENT','MATCHED',policy.matched,'UNKNOWN',policy.unknown,'RESULT',policy.frames[-1].state.name,'LEVELS',policy.frames[-1].levels_completed,'SCORE',fresh_arc.get_scorecard().score,flush=True)
