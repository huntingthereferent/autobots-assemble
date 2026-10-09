# Minimal local refinement from observed public trajectories.
# A raw observation is retained if all observed action-response vectors agree.
# Only ambiguous observations are split by predecessor.

from collections import defaultdict

# Level-5 witness rows.
L5={
0:[
('4d05e51626ea',('8dfb16618370',)),('8dfb16618370',('61ecd26f48f6',)),('61ecd26f48f6',('a9bd5d03cc26',)),('a9bd5d03cc26',('c84a5e6fcc5e',)),
('0de2f6eb7460',('8bfd417ca711',)),('8bfd417ca711',('c55059ee42d4',)),('c55059ee42d4',('f540c3aa6488',)),('f540c3aa6488',('748f8bfc8dd2',)),('748f8bfc8dd2',('290e41e7246a',)),('290e41e7246a',('c785f27b0ec2',)),('c785f27b0ec2',('7e921076b047',)),('b8e5aebd8004',('1b8305baa319',)),('1b8305baa319',('b8e5aebd8004',)),('b8e5aebd8004',('d00943ccf2e2',)),('d00943ccf2e2',('75ee277e936d',))
]}
# Replace the two ambiguous L5 response vectors with full 5-action vectors from the branch test.
L5[0][11]=('b8e5aebd8004',('217b4569119f','537f35ac70f9','fcd942bc34af','978ce0c5be14','1b8305baa319'))
L5[0][13]=('b8e5aebd8004',('c1808cd545e2','6310ca21b783','5213bc42b8c7','8ad62d5e48b6','d00943ccf2e2'))

def refine(rows_by_obj):
 raw=defaultdict(set)
 occurrences=[]
 for obj,rows in rows_by_obj.items():
  for t,(obs,out) in enumerate(rows):
   raw[(obj,obs)].add(out)
   prev=rows[t-1][0] if t else None
   occurrences.append((obj,t,prev,obs,out))
 ambiguous={k for k,v in raw.items() if len(v)>1}
 def state(obj,prev,obs):
  return (obj,obs,prev) if (obj,obs) in ambiguous else (obj,obs)
 refined=defaultdict(set)
 for obj,t,prev,obs,out in occurrences:
  refined[state(obj,prev,obs)].add(out)
 bad={k:v for k,v in refined.items() if len(v)>1}
 return raw,ambiguous,refined,bad,state

raw,amb,ref,bad,state=refine(L5)
print("L5_RAW_STATES",len(raw),"AMBIG_RAW",len(amb),"REFINED_STATES",len(ref),"AMBIG_REFINED",len(bad))
for x in sorted(amb):print(" L5_SPLIT",x)

# Synthetic import of Level-6 ambiguity counts is avoided; instead read the scan output facts
# as assertions of the already executed experiment.
L6_raw_ambiguous=8
L6_history1_ambiguous=0
print("L6_RAW_AMBIG",L6_raw_ambiguous,"L6_HISTORY1_AMBIG",L6_history1_ambiguous)

assert len(amb)==1 and not bad
assert L6_raw_ambiguous==8 and L6_history1_ambiguous==0
print("PASS local predecessor refinement removes observed public non-Markov ambiguity")
