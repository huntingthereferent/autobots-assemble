from arc_agi import Arcade,OperationMode
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
print([x for x in dir(e._game.camera) if "grid" in x.lower() or "display" in x.lower()])
