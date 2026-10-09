from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make('ar25')
print("LOCAL_DIR",e.environment_info.local_dir)
print("CLASS",e.environment_info.class_name)
