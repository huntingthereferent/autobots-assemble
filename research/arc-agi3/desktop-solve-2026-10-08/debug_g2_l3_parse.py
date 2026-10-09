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
def settle():
    for _ in range(7): click((63,63))
def do(moves):
    for src,dst in moves:
        click(src);click(dst);settle()
    return env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
do([((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))])
do([((32,58),(22,22)),((18,58),(28,22)),((10,58),(22,36)),((46,58),(28,36)),((24,58),(34,36)),((52,58),(40,36)),((38,58),(40,22))])
o=do([((52,58),(20,24)),((18,58),(20,36)),((24,58),(26,36)),((32,58),(32,24)),((46,58),(38,36)),((38,58),(44,36)),((10,58),(44,24))])
dummy=object.__new__(m.MyAgent)
print(m.MyAgent._parse_construction(dummy,o))
