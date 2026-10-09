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
# l0
for src,dst in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(src);click(dst);settle()
env.step(GameAction.ACTION5,data={},reasoning={"probe":"e0"})
# l1
src={8:(11,58),15:(18,58),14:(25,58),12:(32,58),6:(39,58),9:(46,58),11:(53,58)}
for c,dst in [(12,(22,22)),(15,(28,22)),(8,(22,36)),(9,(28,36)),(14,(34,36)),(11,(40,36)),(6,(40,22))]:
    click(src[c]);click(dst);settle()
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"e1"})
dummy=object.__new__(m.MyAgent)
print(m.MyAgent._parse_construction(dummy,o))
