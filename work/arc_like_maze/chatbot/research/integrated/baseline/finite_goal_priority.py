from dataclasses import dataclass
ROOT=(0,0,0)
@dataclass(frozen=True)
class Law:
 phi: tuple[int,int,int]
 def step(self,state,action):
  x,y,z=state
  if action=='A':return ((x+1)%3,y,z)
  if action=='B':return (x,(y+x+1)%3,(z+self.phi[y])%3)
  raise ValueError
 def follow(self,word):
  s=ROOT
  for a in word:s=self.step(s,a)
  return s
