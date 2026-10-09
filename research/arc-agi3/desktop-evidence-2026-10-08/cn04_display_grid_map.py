from arc_agi import Arcade,OperationMode
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
for y in [0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400]:
 row=[]
 for x in [0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400]:
  try:g=e._game.camera.display_to_grid(x,y)
  except Exception:g=None
  if g is not None:row.append((x,g))
 if row: print("Y",y,row[:8],"...",row[-3:])
