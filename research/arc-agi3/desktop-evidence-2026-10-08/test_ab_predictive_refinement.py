from ab_predictive_refinement import WitnessedState,ab,equivalent

A=WitnessedState(
 current="b8e5aebd8004",
 predecessor="c785f27b0ec2",
 futures=("217b4569119f","537f35ac70f9","fcd942bc34af","978ce0c5be14","1b8305baa319"),
)
B=WitnessedState(
 current="b8e5aebd8004",
 predecessor="1b8305baa319",
 futures=("c1808cd545e2","6310ca21b783","5213bc42b8c7","8ad62d5e48b6","d00943ccf2e2"),
)
a1,b1=ab(A,B)
print("AB1",a1,b1)
assert not equivalent(a1,b1)
assert a1.current==b1.current=="b8e5aebd8004"
assert dict(a1.retained)["predecessor"]=="c785f27b0ec2"
assert dict(b1.retained)["predecessor"]=="1b8305baa319"

# Reuse outputs as evidence-bearing inputs.  If two occurrences carry the same
# refined state and the same future contract, they collapse.
A2=WitnessedState(current=a1,predecessor=None,futures=("next-x",))
B2=WitnessedState(current=a1,predecessor=None,futures=("next-x",))
x,y=ab(A2,B2)
print("AB2_COLLAPSE",x,y)
assert equivalent(x,y)

# If the same refined output later develops incompatible futures, A/B refuses
# to collapse it without another separating relation.
C2=WitnessedState(current=a1,predecessor="older-left",futures=("next-x",))
D2=WitnessedState(current=a1,predecessor="older-right",futures=("next-y",))
c,d=ab(C2,D2)
print("AB2_LIFT",c,d)
assert not equivalent(c,d)
print("PASS recursive A/B reuse")
