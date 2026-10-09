from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import inspect,copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
base=a.make('ar25');r=None
for z in SOL+MEET:r=base.step(GameAction.from_id(z),data={})
print("ENV_TYPE",type(base))
print("ENV_FILE",inspect.getsourcefile(type(base)))
print("ENV_MODULE",type(base).__module__)
print("RESULT_TYPE",type(r))
print("RESULT_FILE",inspect.getsourcefile(type(r)))
print("RESULT_MODULE",type(r).__module__)
