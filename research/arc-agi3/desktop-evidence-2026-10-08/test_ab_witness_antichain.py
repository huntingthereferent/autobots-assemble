from ab_witness_antichain import WitnessAntichain,ab_compare,factor_core

A1="prev_action1";A2="prev_action2";O1="prev_obs1";O2="prev_obs2"

G=WitnessAntichain.make([(A1,)])
R=WitnessAntichain.make([(A2,),(O1,),(O2,)])
S=WitnessAntichain.make([(A1,),(A2,),(O1,)])
CD=WitnessAntichain.make([(A1,A2),(A1,O1),(A1,O2)])

x=ab_compare(R,S)
print("R_vs_S",x)
assert x.shared_edges==WitnessAntichain.make([(A2,),(O1,)])
assert x.left_only==WitnessAntichain.make([(O2,)])
assert x.right_only==WitnessAntichain.make([(A1,)])

core,res=factor_core(CD)
print("CD_FACTOR",core,res)
assert core==(A1,)
assert res==R

print("G",G,"R",R,"S",S,"CD",CD)
print("PASS witness-antichain A/B")
