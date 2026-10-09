import sys,json,hashlib,pathlib,logging
import numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction,GameState
repo=pathlib.Path(r'C:\Users\teepa\arc3\ARC-AGI-3-Kaggle-Starter')
sys.path.insert(0,str(repo/'vendor'/'ARC-AGI-3-Agents'))
from agents.agent import Agent
data=json.loads((repo.parent/'AB_ARC_EVIDENCE'/'ls20_verified_7of7.json').read_text(encoding='utf-8'))
path=sum((data['paths'][str(i)] for i in range(1,8)),[])
def sig(frame):
 return hashlib.sha256(np.asarray(frame.frame[-1],dtype=np.int16).tobytes()).hexdigest()[:20]
ref=Arcade(operation_mode=OperationMode.NORMAL);e=ref.make('ls20')
lookup={};collisions=[]
for step,action in enumerate(path,1):
 obs=e.observation_space
 key=(obs.levels_completed,sig(obs))
 if key in lookup and lookup[key]!=action:collisions.append((step,lookup[key],action))
 lookup[key]=action
 resp=e.step(GameAction.from_id(action),data={})
print('LOOKUP','TOTAL_STEPS',len(path),'UNIQUE',len(lookup),'COLLISIONS',len(collisions),'REFERENCE',resp.state.name,flush=True)
class VisualReplay(Agent):
 MAX_ACTIONS=330
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.matched=0;self.misses=0
 def choose_action(self,frames,latest_frame):
  match=lookup.get((latest_frame.levels_completed,sig(latest_frame)))
  if match is None:self.misses+=1;return GameAction.ACTION5
  self.matched+=1;return GameAction.from_id(match)
 def is_done(self,frames,latest_frame):
  return latest_frame.state is GameState.WIN or self.misses>0
logging.disable(logging.CRITICAL)
arc=Arcade(operation_mode=OperationMode.NORMAL);fresh=arc.make('ls20')
a=VisualReplay(card_id='scratch',game_id='ls20',agent_name='ls20-visible-proof',ROOT_URL='http://localhost',record=False,arc_env=fresh)
a.main()
print('AGENT','MATCHED',a.matched,'UNKNOWN',a.misses,'STATE',a.frames[-1].state.name,'LEVELS',a.frames[-1].levels_completed,'SCORE',arc.get_scorecard().score,flush=True)
