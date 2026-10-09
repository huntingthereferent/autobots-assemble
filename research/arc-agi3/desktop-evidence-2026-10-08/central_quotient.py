from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
B=[3]; C=[4]; D=[5]; E=[3,4]
def run(seq):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 return o.frame[0].copy(),o
# quotient by central E: x ~ y iff x E^i == y E^j for small earned shifts.
words={'B':B,'C':C,'D':D,'DBD':D+B+D,'DCD':D+C+D,
       'BB':B+B,'CC':C+C,'BD':B+D,'DB':D+B,'CD':C+D,'DC':D+C,
       'BDBD':B+D+B+D,'DBDB':D+B+D+B}
cache={}
for name,w in words.items():
 for k in range(5): cache[(name,k)]=run(w+E*k)
print('QUOTIENT MATCHES MOD CENTRAL E')
for x in words:
 for y in words:
  if x>=y: continue
  hits=[]
  for i in range(5):
   for j in range(5):
    if np.array_equal(cache[(x,i)][0],cache[(y,j)][0]): hits.append((i,j))
  if hits: print(x,'~',y,'shifts',hits[:4])
print('\nCONJUGATION TARGETS')
for x in ['DBD','DCD']:
 b,o=cache[(x,0)]
 best=[]
 for y in ['B','C','D','BB','CC']:
  for j in range(5):
   q=cache[(y,j)][0]; diff=np.count_nonzero(b!=q)
   best.append((diff,y,j))
 print(x,sorted(best)[:6],'L',o.levels_completed,o.state)
# test powers of B modulo E against root/B/C/D; this asks order in quotient.
root,_=run([])
targets={'I':root,'B':run(B)[0],'C':run(C)[0],'D':run(D)[0]}
print('\nB POWERS MOD E')
for n in range(1,13):
 bn,o=run(B*n)
 hits=[]
 for t,tb in targets.items():
  for k in range(5):
   ek,_=run(([] if t=='I' else {'B':B,'C':C,'D':D}[t])+E*k)
   if np.array_equal(bn,ek): hits.append((t,k))
 print(n,'hits',hits,'L',o.levels_completed,o.state)
