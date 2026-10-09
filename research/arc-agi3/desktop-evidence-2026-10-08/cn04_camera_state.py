from arc_agi import Arcade,OperationMode
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
print(e._game.camera.__dict__)
