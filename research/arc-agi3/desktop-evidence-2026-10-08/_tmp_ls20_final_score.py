from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
p5=(1,3,1,1,3,3,3,4,3,4,3,4,1,1,3,3,3,3,1,3,3,3,4,4,2,2,2,2,2,4,4,3,2,2,4,2,4,4,4,4,4,4,4,1)
p6=(1,1,2,1,2,4,4,1,4,1,1,1,3,3,4,4,1,1,4,4,1,1,4,2,2,1,1,3,1,2,3,3,3,3,1,2,3,3,2,2,2,2,1,4,4,4,3,3,3,1,1,1,1,1,1,4,4,4,4,4,4,2,4,4,1,1,4,2,2,2,2,2)
p7=(1,1,2,2,3,3,2,2,2,2,2,1,2,4,4,1,2,1,2,3,2,1,4,1,2,3,3,1,1,1,4,4,4,4,1,4,4,1,4,4,1,1,4,2,2,3,3,3,1,2,2,2,2)
import json
from pathlib import Path
paths=(p1,p2,p3,p4,p5,p6,p7)
base=(22,123,73,84,96,192,186)
arc=Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make('ls20')
for a in sum(paths,()):
 r=env.step(GameAction.from_id(a),data={})
score=arc.get_scorecard()
lengths=[len(p) for p in paths]
print('SCORE',score.score,'STATE',r.state.name,'LEVELS',r.levels_completed,'ACTIONS',sum(lengths),'EACH_LEVEL',lengths,'REFERENCE',base,'FASTER_ALL',all(a<b for a,b in zip(lengths,base)),flush=True)
record={'game':'ls20','method':'local ARC environment replay','status':r.state.name,'levels':r.levels_completed,'score':score.score,'total_actions':sum(lengths),'baseline_actions':list(base),'per_level_actions':lengths,'paths':{str(i+1):list(p) for i,p in enumerate(paths)},'milestones':list(__import__('itertools').accumulate(lengths))}
out=Path(r'C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ls20_verified_7of7.json')
out.write_text(json.dumps(record,indent=2),encoding='utf-8')
print('RECORD_SAVED',str(out),flush=True)
