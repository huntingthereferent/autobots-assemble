from arc_agi import Arcade,OperationMode
import inspect,re
games=["bp35","dc22","cd82","sk48"]
arc=Arcade(operation_mode=OperationMode.NORMAL)
for name in games:
    e=arc.make(name); cls=e._game.__class__
    src=inspect.getsource(cls)
    print("\n###",name,cls.__name__)
    lines=src.splitlines()
    for i,line in enumerate(lines):
        if "ACTION6" in line:
            lo=max(0,i-6); hi=min(len(lines),i+28)
            for j in range(lo,hi): print(f"{j+1:04d}: {lines[j]}")
            break
