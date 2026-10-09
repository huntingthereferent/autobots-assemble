from arc_agi import Arcade,OperationMode
from arcengine import GameAction,GameState
import sys,ast,hashlib,numpy as np,pathlib,logging
from collections import Counter
repo=pathlib.Path(r'C:\Users\teepa\arc3\ARC-AGI-3-Kaggle-Starter')
sys.path.insert(0,str(repo/'vendor'/'ARC-AGI-3-Agents'))
# Import again after path setup:
from agents.agent import Agent
src=(pathlib.Path(r'C:\Users\teepa\arc3\AB_ARC_EVIDENCE\_tmp_sk48_complete_replay.py')).read_text(encoding='utf-8')
tree=ast.parse(src);table={}
for node in tree.body:
 if isinstance(node,ast.Assign):
  for target in node.targets:
   if isinstance(target,ast.Name) and target.id in ('p1','p2','p3','p4','p5','P6','P7','P8'):
    table[target.id]=ast.literal_eval(node.value)
path=sum((table[k] for k in ('p1','p2','p3','p4','p5','P6','P7','P8')),())
clicks={174:(31,4),187:(7,34),202:(37,4),212:(31,4),222:(7,28),224:(37,4),227:(7,22),236:(31,4),238:(7,28),240:(31,4),243:(7,34),259:(31,4),271:(7,28)}
def signature(frame):
 a=np.asarray(frame.frame[-1],dtype=np.int16)
 return hashlib.sha256(a.tobytes()).hexdigest()[:18]
def run_action(env,index,z):
 d={} if z!=6 else {'x':clicks[index][0],'y':clicks[index][1]}
 return env.step(GameAction.from_id(z),data=d)
training=Arcade(operation_mode=OperationMode.NORMAL); env=training.make('sk48')
lookup={}
for i,z in enumerate(path,1):
 obs=env.observation_space
 key=(obs.levels_completed,signature(obs))
 action=(z,clicks.get(i))
 if key in lookup and lookup[key]!=action:raise AssertionError(('collision',i,key))
 lookup[key]=action
 r=run_action(env,i,z)
print('REFERENCE','steps',len(path),'unique_visible_keys',len(lookup),'result',r.state.name,flush=True)
class VisiblePolicy(Agent):
 MAX_ACTIONS=320
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.matched=0;self.unknown=0
 def is_done(self,frames,latest_frame):
  return latest_frame.state is GameState.WIN or self.unknown>0
 def choose_action(self,frames,latest_frame):
  key=(latest_frame.levels_completed,signature(latest_frame))
  action=lookup.get(key)
  if action is None:
   self.unknown+=1
   return GameAction.ACTION5
  self.matched+=1
  z,xy=action
  step=GameAction.from_id(z)
  if z==6:step.set_data({'x':xy[0],'y':xy[1]})
  return step
logging.disable(logging.CRITICAL)
fresh=Arcade(operation_mode=OperationMode.NORMAL);freshenv=fresh.make('sk48')
agent=VisiblePolicy(card_id='scratch',game_id='sk48',agent_name='visible-lookup-proof',ROOT_URL='http://localhost',record=False,arc_env=freshenv)
agent.main()
last=agent.frames[-1]
print('VISIBLE_AGENT','matched',agent.matched,'unknown',agent.unknown,'state',last.state.name,'completed',last.levels_completed,'score',fresh.get_scorecard().score,'steps',agent.action_counter,flush=True)
control=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
key=(control.observation_space.levels_completed,signature(control.observation_space))
print('LS20_TRANSFER','initial_key_in_SK48_map',key in lookup,'prediction',lookup.get(key),flush=True)
