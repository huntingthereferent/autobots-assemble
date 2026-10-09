from causal_operator_model import infer_fixed_relation,infer_controlled_relation

# Level 1: no controllable axis, source intervention alone.
fixed=infer_fixed_relation(
 "x",base_source=7.4,base_dependent=12.6,
 delta_source=1,delta_dependent=-1,
)
assert fixed.is_reflection_signature()
assert abs(fixed.reflection_axis()-10)<1e-9
assert abs(fixed.dependent(8.4)-11.6)<1e-9

# Level 2: axis intervention + payload intervention.
mov=infer_controlled_relation(
 "x",base_source=17,base_control=12,base_dependent=7,
 delta_source=1,dq_from_source=-1,
 delta_control=1,dq_from_control=2,
)
assert mov.is_reflection_signature()
assert mov.reflection_axis(12)==12
assert mov.dependent(18,12)==6
assert mov.dependent(17,13)==9
print("PASS fixed",fixed,"movable",mov)
