from __future__ import annotations

from math import factorial
from random import Random
from typing import Any

FAMILIES = ("transform","solve","compare","represent","measure","infer")
DOMAINS = (
    "number","number-theory","algebra","functions","sequences","exponents-logarithms",
    "geometry","analytic-geometry","trigonometry","vectors","complex-numbers",
    "linear-algebra","sets-logic","combinatorics","probability","statistics",
    "calculus","differential-equations","financial-math",
)

ALIASES = {
    "numbers":"number","number theory":"number-theory","function":"functions",
    "sequence":"sequences","logs":"exponents-logarithms","logarithms":"exponents-logarithms",
    "analytic geometry":"analytic-geometry","coordinate geometry":"analytic-geometry",
    "trig":"trigonometry","vector":"vectors","complex":"complex-numbers",
    "linear algebra":"linear-algebra","matrix":"linear-algebra","matrices":"linear-algebra",
    "sets":"sets-logic","logic":"sets-logic","combinations":"combinatorics",
    "permutations":"combinatorics","probability and statistics":"statistics","stats":"statistics",
    "derivatives":"calculus","integrals":"calculus","differential equations":"differential-equations",
    "finance":"financial-math",
}

def normalize_domain(value: Any) -> str:
    text=str(value or "").strip().lower().replace("_","-")
    text=ALIASES.get(text,text)
    return text if text in DOMAINS else "algebra"

def _item(prompt,answer,why,family,domain):
    return {"prompt":prompt,"answer":f"{answer}\nWhy: {why}","kind":"math","lines":2,
            "math_family":family,"math_domain":domain}

def _number(rng,family):
    a,b=rng.randint(12,99),rng.randint(2,12)
    if family=="compare":
        return _item(f"Which is greater: {a} or {a+b}?",str(a+b),"Compare their values.",family,"number")
    if family=="represent":
        return _item(f"Write {a} as tens and ones.",f"{a//10} tens and {a%10} ones","Use base-10 place value.",family,"number")
    return _item(f"Evaluate {a} + {b} × 2.",str(a+b*2),"Apply multiplication before addition.",family,"number")

def _number_theory(rng,family):
    import math
    a=rng.choice((24,30,36,42,48,60,72)); b=rng.choice((18,24,30,36,54))
    if family in {"solve","infer"}:
        return _item(f"Find gcd({a}, {b}).",str(math.gcd(a,b)),"Use common prime factors or Euclid's algorithm.",family,"number-theory")
    return _item(f"Is {a} divisible by 6? Explain.","Yes" if a%6==0 else "No","Check divisibility by both 2 and 3.",family,"number-theory")

def _algebra(rng,family):
    x=rng.randint(2,12); m=rng.randint(2,9); b=rng.randint(1,12); total=m*x+b
    if family=="transform":
        return _item(f"Expand 3(x + {b}).",f"3x + {3*b}","Distribute 3 to both terms.",family,"algebra")
    if family=="represent":
        return _item(f"Write an equation for: {m} times a number plus {b} equals {total}.",f"{m}x + {b} = {total}","Translate the relation into symbols.",family,"algebra")
    return _item(f"Solve {m}x + {b} = {total}.",str(x),f"Subtract {b}, then divide by {m}.",family,"algebra")

def _functions(rng,family):
    m=rng.randint(2,7); b=rng.randint(-5,5); x=rng.randint(-4,6); y=m*x+b
    if family=="compare":
        return _item(f"For f(x)={m}x+{b}, compare f({x}) and f({x+1}).",f"f({x+1}) is greater by {m}","A linear function changes by its slope.",family,"functions")
    if family=="represent":
        return _item(f"For f(x)={m}x+{b}, state the slope and y-intercept.",f"slope={m}, y-intercept={b}","Use y=mx+b.",family,"functions")
    return _item(f"If f(x)={m}x+{b}, find f({x}).",str(y),"Substitute the input for x.",family,"functions")

def _sequences(rng,family):
    a=rng.randint(1,10); d=rng.randint(2,8); n=rng.randint(5,12)
    return _item(f"An arithmetic sequence starts at {a} with common difference {d}. Find term {n}.",str(a+(n-1)*d),"Use a_n=a_1+(n-1)d.",family,"sequences")

def _logs(rng,family):
    base=rng.choice((2,3,5)); exp=rng.randint(2,5); value=base**exp
    if family=="transform":
        return _item(f"Rewrite {base}^{exp}={value} in logarithmic form.",f"log_{base}({value})={exp}","Exponential and logarithmic forms are inverse descriptions.",family,"exponents-logarithms")
    return _item(f"Solve {base}^x={value}.",str(exp),"Match powers of the same base.",family,"exponents-logarithms")

def _geometry(rng,family):
    r=rng.randint(2,10)
    if family=="measure":
        return _item(f"A circle has radius {r}. Give its area in terms of pi.",f"{r*r}pi","Use A=pi*r^2.",family,"geometry")
    return _item("A right triangle has legs 3 and 4. Find the hypotenuse.","5","Use a^2+b^2=c^2.",family,"geometry")

def _analytic_geometry(rng,family):
    x1,y1=rng.randint(-5,2),rng.randint(-5,2); x2,y2=x1+rng.randint(2,6),y1+rng.randint(2,6)
    if family=="measure":
        return _item(f"Find the midpoint of ({x1},{y1}) and ({x2},{y2}).",f"({(x1+x2)/2:g},{(y1+y2)/2:g})","Average corresponding coordinates.",family,"analytic-geometry")
    return _item(f"Find the slope through ({x1},{y1}) and ({x2},{y2}).",f"{y2-y1}/{x2-x1}","Use (y2-y1)/(x2-x1).",family,"analytic-geometry")

def _trigonometry(rng,family):
    angle,ans=rng.choice((("30 degrees","1/2"),("45 degrees","sqrt(2)/2"),("60 degrees","sqrt(3)/2")))
    return _item(f"Evaluate sin({angle}).",ans,"Use the special-angle unit-circle values.",family,"trigonometry")

def _vectors(rng,family):
    a,b,c,d=[rng.randint(-5,5) for _ in range(4)]
    if family=="measure":
        return _item(f"Find the magnitude of v=<{a},{b}>.",f"sqrt({a*a+b*b})","Use ||v||=sqrt(a^2+b^2).",family,"vectors")
    return _item(f"Add <{a},{b}> + <{c},{d}>.",f"<{a+c},{b+d}>","Add corresponding components.",family,"vectors")

def _complex(rng,family):
    a,b,c,d=[rng.randint(-5,5) for _ in range(4)]
    return _item(f"Add ({a}+{b}i)+({c}+{d}i).",f"{a+c}+{b+d}i","Combine real and imaginary parts separately.",family,"complex-numbers")

def _linear_algebra(rng,family):
    a,b,c,d=[rng.randint(1,6) for _ in range(4)]
    if family in {"measure","infer"}:
        return _item(f"Find det([[{a},{b}],[{c},{d}]]).",str(a*d-b*c),"For a 2x2 matrix, det=ad-bc.",family,"linear-algebra")
    return _item(f"Add [[{a},{b}],[{c},{d}]] and the identity matrix.",f"[[{a+1},{b}],[{c},{d+1}]]","Add corresponding entries.",family,"linear-algebra")

def _sets_logic(rng,family):
    return _item("If A is a subset of B and x is in A, what must be true?","x is in B","Every element of a subset belongs to the containing set.",family,"sets-logic")

def _combinatorics(rng,family):
    n=rng.randint(5,8); r=rng.randint(2,min(4,n)); ans=factorial(n)//(factorial(r)*factorial(n-r))
    return _item(f"How many ways can you choose {r} objects from {n} distinct objects?",str(ans),"Use C(n,r)=n!/[r!(n-r)!].",family,"combinatorics")

def _probability(rng,family):
    red=rng.randint(2,8); blue=rng.randint(2,8)
    return _item(f"A bag has {red} red and {blue} blue tokens. Find P(red).",f"{red}/{red+blue}","Probability=favorable outcomes/total outcomes.",family,"probability")

def _statistics(rng,family):
    vals=[rng.randint(1,20) for _ in range(5)]
    if family=="infer":
        return _item(f"Data: {vals}. Which measure gives the arithmetic center?","mean","The mean averages all observed values.",family,"statistics")
    return _item(f"Find the mean of {vals}.",f"{sum(vals)/len(vals):g}","Add the values and divide by the count.",family,"statistics")

def _calculus(rng,family):
    a=rng.randint(2,8); n=rng.randint(2,5)
    if family=="measure":
        return _item(f"Integrate {a}x^{n} dx.",f"{a}/{n+1} x^{n+1} + C","Increase the exponent by 1 and divide by the new exponent.",family,"calculus")
    return _item(f"Differentiate f(x)={a}x^{n}.",f"f'(x)={a*n}x^{n-1}","Apply the power rule.",family,"calculus")

def _differential_equations(rng,family):
    k=rng.randint(1,5)
    return _item(f"Solve dy/dx={k}y in general form.",f"y=C*e^({k}x)","Separate variables and integrate, or recognize exponential growth.",family,"differential-equations")

def _financial(rng,family):
    p=rng.choice((1000,1500,2000,5000)); rate=rng.choice((0.03,0.04,0.05)); years=rng.randint(2,5)
    amount=p*((1+rate)**years)
    return _item(f"{p} dollars is invested at {rate*100:g}% compounded annually for {years} years. Find the balance.",f"{amount:.2f} dollars","Use A=P(1+r)^t.",family,"financial-math")

BUILDERS={
    "number":_number,"number-theory":_number_theory,"algebra":_algebra,"functions":_functions,
    "sequences":_sequences,"exponents-logarithms":_logs,"geometry":_geometry,
    "analytic-geometry":_analytic_geometry,"trigonometry":_trigonometry,"vectors":_vectors,
    "complex-numbers":_complex,"linear-algebra":_linear_algebra,"sets-logic":_sets_logic,
    "combinatorics":_combinatorics,"probability":_probability,"statistics":_statistics,
    "calculus":_calculus,"differential-equations":_differential_equations,"financial-math":_financial,
}

def infer_domain(prompt: Any, explicit: Any="") -> str:
    if str(explicit or "").strip(): return normalize_domain(explicit)
    text=str(prompt or "").lower()
    probes=(
        ("differential equation","differential-equations"),("derivative","calculus"),("integral","calculus"),("calculus","calculus"),
        ("matrix","linear-algebra"),("determinant","linear-algebra"),("vector","vectors"),("complex","complex-numbers"),
        ("trig","trigonometry"),("sine","trigonometry"),("cosine","trigonometry"),("log","exponents-logarithms"),
        ("sequence","sequences"),("probability","probability"),("statistics","statistics"),("mean","statistics"),
        ("combination","combinatorics"),("permutation","combinatorics"),("set ","sets-logic"),("logic","sets-logic"),
        ("number theory","number-theory"),("divisib","number-theory"),("coordinate","analytic-geometry"),
        ("finance","financial-math"),("interest","financial-math"),("function","functions"),("geometry","geometry"),
        ("algebra","algebra"),("equation","algebra"),
    )
    return next((domain for needle,domain in probes if needle in text),"algebra")

def infer_family(prompt: Any, explicit: Any="") -> str:
    text=str(explicit or "").strip().lower()
    if text in FAMILIES: return text
    p=str(prompt or "").lower()
    checks=(("solve","solve"),("simplif","transform"),("rewrite","transform"),("expand","transform"),
            ("compare","compare"),("represent","represent"),("graph","represent"),("measure","measure"),
            ("area","measure"),("length","measure"),("probability","infer"),("infer","infer"),("estimate","infer"))
    return next((family for needle,family in checks if needle in p),"solve")

def generate_math_space(payload: dict[str,Any], rng: Random):
    prompt=payload.get("math_prompt") or payload.get("topic") or ""
    domain=infer_domain(prompt,payload.get("math_domain"))
    family=infer_family(prompt,payload.get("math_family"))
    try: count=max(1,min(60,int(payload.get("count") or 10)))
    except (TypeError,ValueError): count=10
    builder=BUILDERS[domain]; out=[]; seen=set(); tries=0
    while len(out)<count and tries<count*40:
        tries+=1; row=builder(rng,family); key=(row["prompt"],row["answer"])
        if key in seen: continue
        seen.add(key); out.append(row)
    if not out: raise ValueError("could not generate math-space problems")
    base=list(out)
    while len(out)<count:
        row=dict(base[len(out)%len(base)])
        row["prompt"]=f"{row['prompt']}  [variant {len(out)+1}]"
        out.append(row)
    return {"family":family,"domain":domain,"count":count,"unbounded":True,
            "families":FAMILIES,"domains":DOMAINS},out
