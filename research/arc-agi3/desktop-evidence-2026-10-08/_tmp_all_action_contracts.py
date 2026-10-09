from arc_agi import Arcade,OperationMode
games="ar25 bp35 cd82 cn04 dc22 ft09 g50t ka59 lf52 lp85 ls20 m0r0 r11l re86 s5i5 sb26 sc25 sk48 sp80 su15 tn36 tr87 tu93 vc33 wa30".split()
arc=Arcade(operation_mode=OperationMode.NORMAL)
for name in games:
 try:
  e=arc.make(name)
  acts=list(e._last_response.available_actions)
  vals=[getattr(a,"value",a) for a in acts]
  print(name,vals,"COMPLEX6",6 in vals)
 except Exception as ex:
  print(name,"ERR",type(ex).__name__,str(ex)[:100])
