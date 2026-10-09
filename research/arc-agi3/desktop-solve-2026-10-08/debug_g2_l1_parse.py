import importlib.util,sys,arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

spec=importlib.util.spec_from_file_location("g2",r"C:\Users\teepa\arc3\solve\my_agent_g2.py")
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
def click(p):
    a=GameAction.ACTION6;a.set_data({"x":p[0],"y":p[1]})
    return env.step(a,data=a.action_data.model_dump(),reasoning={"probe":"prep"})
for src,dst in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(src);click(dst)
    for _ in range(7):click((63,63))
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
dummy=object.__new__(m.MyAgent)
parsed=m.MyAgent._parse_construction(dummy,o)
print(parsed)
