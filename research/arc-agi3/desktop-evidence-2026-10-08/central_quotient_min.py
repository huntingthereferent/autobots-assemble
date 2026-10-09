from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); p=[3]*5+[2]*10
def r(s):
 e=a.make('ar25')
 for x in p+s:o=e.step(GameAction.from_id(x),data={})
 return o.frame[0].copy(),o
B=[3];C=[4];D=[5];E=[3,4]
tests={
 'DBD':D+B+D,'C':C,'C+E':C+E,
 'DCD':D+C+D,'B':B,'B+E':B+E,
 'D2':D+D,'E':E,
 'BC':B+C,'CB':C+B,
 'BDBD':B+D+B+D,'DBDB':D+B+D+B,
}
z={k:r(v) for k,v in tests.items()}
print('exact witnesses')
for x,y in [('DBD','C'),('DBD','C+E'),('DCD','B'),('DCD','B+E'),('D2','E'),('BC','E'),('CB','E'),('BDBD','E'),('DBDB','E')]:
 print(x,y,'eq',np.array_equal(z[x][0],z[y][0]),'diff',np.count_nonzero(z[x][0]!=z[y][0]))
print('levels',[(k,v[1].levels_completed,str(v[1].state)) for k,v in z.items()])
