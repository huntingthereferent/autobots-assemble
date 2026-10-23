# Two-predecessor transition schema — exact shear test

## Mathematical question

The existing process schema writes every B increment at coordinate i >= 2 as a one-input rule p_(i-2)(x_(i-1)), with p(0)=0. The already-constructed non-diagonal map

H_c(x_0,x_1,x_2,x_3,...) = (x_0,x_1,x_2+c*x_1^2,x_3,...)

produces an exactly conjugate action, but the transformed increment at coordinate 2 depends on both x_0 and x_1. Coordinate 3 also needs the transformed input x_2-c*x_1^2.

## Smallest uniform local widening

Use a table q_i : F_3 x F_3 -> F_3 for each B increment:

B(x)_0 = x_0
B(x)_1 = x_1 + g*(x_0+1)
B(x)_i = x_i + q_i(x_(i-2), x_(i-1)) mod 3, for i >= 2.

The old schema embeds by q_i(u,v)=p_(i-2)(v), so it is a strict subfamily. For the shear H_c, the exact transformed tables are:

q_2(u,v) = p_0(v) + c*((v+g*(u+1))^2-v^2) mod 3
q_3(u,v) = p_1(v-c*u^2) mod 3
q_i(u,v) = p_(i-2)(v) mod 3, for i >= 4.

No approximations are used. These equations follow directly from H_c B H_(-c). The coordinate-2 obstruction is literal: for c in {1,2}, q_2(0,0)=c while q_2(2,0)=0. Thus no function of v alone can represent q_2. The schema mismatch does not imply non-equivalence; H_(e-c) remains an explicit conjugacy between parameters c and e.

## Executed finite checks

The test suite exhausts every state in F_3^d for d=3,4,5 across four rule streams, both root gains, all three shear coefficients, and both actions. It compares the two-input table implementation against the separate direct conjugation implementation. It also checks all ordered shear-to-shear conjugacies and the exact one-input obstruction.

The finite state comparisons are bounded implementation checks. The displayed algebraic formulas give the general all-depth derivation for this declared shear family; they do not classify arbitrary non-diagonal transformations or establish universal A/B closure.

Run from repository root:

```sh
python -m unittest network.tests.test_arc_like_two_predecessor_schema -v
```
