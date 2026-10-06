from __future__ import annotations
from fractions import Fraction
from math import gcd
from random import Random
from typing import Any
import re

TOPICS = (
    "addition","subtraction","multiplication","division","mixed","fractions",
    "decimals","percent","algebra","geometry","time","money","measurement",
    "place-value","comparison","patterns","word-problems",
)
QUESTION_TYPES = ("short-answer","single-choice","fill-blank","mixed")

def clean(v: Any) -> str:
    return str(v or "").strip()

def grade_number(v: Any) -> int | None:
    t=clean(v).lower()
    if not t or t=="auto": return None
    if t in {"adult","unbounded"}: return 12
    if t in {"k","kg","kindergarten"}: return 0
    m=re.search(r"(\d+)",t)
    return max(0,min(12,int(m.group(1)))) if m else None

def infer_spec(p: dict[str,Any]) -> dict[str,Any]:
    prompt=clean(p.get("math_prompt") or p.get("topic")).lower()
    grade=grade_number(p.get("grade"))
    if grade is None:
        m=re.search(r"(\d+)(?:st|nd|rd|th)?\s*grade",prompt)
        grade=int(m.group(1)) if m else (0 if "kindergarten" in prompt else 3)
    topic=clean(p.get("math_topic")).lower()
    aliases={"fraction":"fractions","decimal":"decimals","equation":"algebra","equations":"algebra",
             "word problem":"word-problems","word problems":"word-problems","place value":"place-value",
             "compare":"comparison","pattern":"patterns"}
    topic=aliases.get(topic,topic)
    if not topic or topic=="auto":
        if (("addition" in prompt or "add " in prompt) and
                ("subtraction" in prompt or "subtract" in prompt)):
            topic = "mixed"
        if topic != "mixed":
            checks=[("word problem","word-problems"),("equal share","fractions"),("halves","fractions"),("fourths","fractions"),("fraction","fractions"),("decimal","decimals"),
                    ("percent","percent"),("algebra","algebra"),("equation","algebra"),
                    ("geometry","geometry"),("area","geometry"),("perimeter","geometry"),
                    ("time","time"),("clock","time"),("money","money"),("coin","money"),
                    ("measurement","measurement"),("place value","place-value"),("compare","comparison"),
                    ("pattern","patterns"),("multiply","multiplication"),("multiplication","multiplication"),
                    ("divide","division"),("division","division"),("subtract","subtraction"),
                    ("subtraction","subtraction"),("add","addition"),("addition","addition")]
            topic=next((mapped for needle,mapped in checks if needle in prompt),"mixed")
    if topic not in TOPICS: topic="mixed"
    m=re.search(r"within\s+(\d+)",prompt)
    within=max(1,int(m.group(1))) if m else None
    try: count=max(1,min(60,int(p.get("count") or 10)))
    except (TypeError,ValueError): count=10
    q=clean(p.get("question_type")).lower() or "short-answer"
    q={"single choice":"single-choice","fill blank":"fill-blank"}.get(q,q)
    if q not in QUESTION_TYPES: q="short-answer"
    constraints={
        "halves_fourths": "halves and fourths" in prompt or "two or four equal shares" in prompt,
        "hour_half_hour": "hour and half-hour" in prompt or "hour and half hour" in prompt,
        "coin_values": "coin values" in prompt or all(x in prompt for x in ("penny","nickel","dime","quarter")),
        "equal_groups": "equal groups" in prompt,
        "sharing_grouping": "sharing and grouping" in prompt,
        "two_step": "two-step" in prompt or "two step" in prompt,
    }
    return {"grade":grade,"topic":topic,"within":within,"count":count,
            "question_type":q,"difficulty":clean(p.get("level")).lower() or "standard",
            "prompt":clean(p.get("math_prompt") or p.get("topic")),
            "constraints":constraints}

def bounds(grade:int,difficulty:str,within:int|None):
    base={0:(5,5),1:(20,10),2:(100,12),3:(1000,12),4:(10000,12),5:(100000,20),6:(1000000,25)}
    add,mult=base.get(min(grade,6),(1000000,30))
    explicit_within = within is not None
    if explicit_within: add=within
    if difficulty=="support":
        add=max(5,add//2) if not explicit_within else add
        mult=max(5,mult//2)
    if difficulty=="challenge":
        if not explicit_within: add*=2
        mult=max(mult,15)
    return add,mult

def item(prompt,answer,why,kind="math",choices=()):
    if choices:
        prompt += "\n" + "\n".join(f"{chr(65+i)}. {x}" for i,x in enumerate(choices))
    return {"prompt":prompt,"answer":f"{answer}\nWhy: {why}","kind":kind,
            "lines":2 if kind=="response" else 1}

def distractors(answer:str,rng:Random):
    try:
        if "/" in answer:
            f=Fraction(answer); pool={str(Fraction(f.numerator+1,f.denominator)),
                                     str(Fraction(max(1,f.numerator-1),f.denominator)),
                                     str(Fraction(f.numerator,f.denominator+1))}
        elif "." in answer and "$" not in answer:
            n=float(answer); pool={f"{n+.1:.2f}".rstrip("0").rstrip("."),
                                  f"{max(0,n-.1):.2f}".rstrip("0").rstrip("."),
                                  f"{n+1:.2f}".rstrip("0").rstrip(".")}
        else:
            suffix="%" if "%" in answer else ""; prefix="$" if "$" in answer else ""
            n=int(float(answer.replace("$","").replace("%","")))
            pool={f"{prefix}{n+d}{suffix}" for d in (-2,-1,1,2) if n+d>=0}
    except Exception: pool={"None of these","Cannot be determined","Not enough information"}
    pool.discard(answer); vals=[answer]+list(pool)[:3]
    while len(vals)<4: vals.append("None of these")
    rng.shuffle(vals); return tuple(vals)

def format_question(x:dict,qtype:str,rng:Random):
    q=qtype if qtype!="mixed" else rng.choice(("short-answer","single-choice","fill-blank"))
    if q=="single-choice":
        ans=x["answer"].split("\n",1)[0]
        x["prompt"] += "\n" + "\n".join(f"{chr(65+i)}. {c}" for i,c in enumerate(distractors(ans,rng)))
        x["kind"]="choice"
    elif q=="fill-blank":
        x["prompt"]=x["prompt"].replace("=","= ____") if "=" in x["prompt"] else x["prompt"]+" ____"
    return x

def arithmetic(topic,grade,difficulty,within,rng):
    add,mult=bounds(grade,difficulty,within)
    if topic=="mixed":
        ops=["addition","subtraction"]+(["multiplication","division"] if grade>=3 else [])
        topic=rng.choice(ops)
    if topic=="addition":
        a=rng.randint(0,add)
        b=rng.randint(0,max(0,add-a)) if within is not None else rng.randint(0,add)
        return item(f"{a} + {b} =",str(a+b),f"Add {a} and {b}.")
    if topic=="subtraction":
        a,b=rng.randint(0,add),rng.randint(0,add); a,b=max(a,b),min(a,b)
        return item(f"{a} − {b} =",str(a-b),f"Subtract {b} from {a}.")
    if topic=="multiplication":
        a,b=rng.randint(0,mult),rng.randint(0,mult)
        return item(f"{a} × {b} =",str(a*b),f"{a} groups of {b} equals {a*b}.")
    d=rng.randint(1,max(2,mult)); q=rng.randint(1,max(2,mult)); n=d*q
    return item(f"{n} ÷ {d} =",str(q),f"{d} × {q} = {n}, so {n} ÷ {d} = {q}.")

def fractions(grade,difficulty,rng,constraints=None):
    constraints=constraints or {}
    if constraints.get("halves_fourths"):
        d=rng.choice((2,4)); n=rng.randint(1,d-1); shape=rng.choice(("circle","rectangle"))
        word="halves" if d==2 else "fourths"
        return item(f"A {shape} is split into {d} equal parts. {n} part(s) are selected. What fraction of the whole is selected?",
                    f"{n}/{d}",f"{d} equal parts are {word}; {n} selected part(s) is {n}/{d}.")
    denmax=6 if grade<=3 else (20 if difficulty=="challenge" else 12)
    d=rng.randint(2,denmax)
    if grade<=3:
        n=rng.randint(1,d-1)
        return item(f"Which fraction names {n} out of {d} equal parts?",f"{n}/{d}",
                    f"{n} selected parts out of {d} total parts is {n}/{d}.")
    d2=d if difficulty=="support" else rng.randint(2,denmax)
    a,b=rng.randint(1,d-1),rng.randint(1,d2-1)
    r=Fraction(a,d)+Fraction(b,d2); common=d*d2//gcd(d,d2)
    return item(f"{a}/{d} + {b}/{d2} =",str(r),
                f"Use common denominator {common}, add equivalent fractions, then simplify.")

def decimals(grade,rng):
    places=1 if grade<=4 else 2; scale=10**places
    a,b=rng.randint(1,20*scale),rng.randint(1,20*scale)
    if rng.choice((True,False)):
        return item(f"{a/scale:.{places}f} + {b/scale:.{places}f} =",f"{(a+b)/scale:.{places}f}",
                    "Line up decimal places, then add.")
    a,b=max(a,b),min(a,b)
    return item(f"{a/scale:.{places}f} − {b/scale:.{places}f} =",f"{(a-b)/scale:.{places}f}",
                "Line up decimal places, then subtract.")

def percent(rng):
    pct=rng.choice((10,20,25,50,75)); base=rng.choice((20,40,60,80,100,120,200)); ans=base*pct//100
    return item(f"What is {pct}% of {base}?",str(ans),f"Multiply {base} by {pct}/100 to get {ans}.")

def algebra(grade,difficulty,rng):
    x=rng.randint(1,50 if difficulty=="challenge" else 20); a=rng.randint(1,12)
    if grade<=5:
        total=x+a
        return item(f"x + {a} = {total}. Find x.",str(x),f"Subtract {a}: x = {total} − {a} = {x}.")
    m=rng.randint(2,9); b=rng.randint(0,12); total=m*x+b
    return item(f"{m}x + {b} = {total}. Find x.",str(x),
                f"Subtract {b}, then divide by {m}: x = {x}.")

def geometry(grade,rng):
    if grade<=2:
        name,sides=rng.choice((("triangle",3),("square",4),("pentagon",5),("hexagon",6)))
        return item(f"How many sides does a {name} have?",str(sides),f"A {name} has {sides} sides.")
    w,h=rng.randint(2,15),rng.randint(2,15)
    if rng.choice((True,False)):
        return item(f"A rectangle is {w} by {h} units. What is its area?",str(w*h),
                    f"Area = {w} × {h} = {w*h} square units.")
    return item(f"A rectangle is {w} by {h} units. What is its perimeter?",str(2*(w+h)),
                f"Perimeter = 2({w}+{h}) = {2*(w+h)} units.")

def time_problem(rng,constraints=None):
    constraints=constraints or {}
    if constraints.get("hour_half_hour"):
        h=rng.randint(1,12); m=rng.choice((0,30))
        return item(f"Write the time shown in words: {h}:{m:02d}.",
                    f"{h} o'clock" if m==0 else f"half past {h}",
                    "Times ending in :00 are on the hour; times ending in :30 are half past the hour.")
    h=rng.randint(1,12); m=rng.choice((0,5,10,15,20,25,30,35,40,45,50,55)); delta=rng.choice((15,30,45,60,90))
    total=(h%12)*60+m+delta; h2=(total//60)%12 or 12; m2=total%60
    return item(f"It is {h}:{m:02d}. What time will it be in {delta} minutes?",f"{h2}:{m2:02d}",
                f"Add {delta} minutes to {h}:{m:02d}.")

def money(rng,constraints=None):
    constraints=constraints or {}
    if constraints.get("coin_values"):
        coin,value=rng.choice((("penny",1),("nickel",5),("dime",10),("quarter",25)))
        if rng.choice((True,False)):
            return item(f"How many cents is a {coin} worth?",str(value),f"A {coin} is worth {value} cents.")
        return item(f"Which coin is worth {value} cents?",coin,f"The {coin} is worth {value} cents.")
    cents=rng.randint(50,1800); price=cents/100; paid=rng.choice((5,10,20))
    while paid*100<cents: paid*=2
    change=paid-price
    return item(f"An item costs ${price:.2f}. You pay with ${paid:.2f}. How much change?",
                f"${change:.2f}", f"Change = ${paid:.2f} − ${price:.2f} = ${change:.2f}.")

def measurement(rng):
    n=rng.randint(1,20); unit,factor,target=rng.choice((("feet",12,"inches"),("yards",3,"feet"),("hours",60,"minutes")))
    return item(f"Convert {n} {unit} to {target}.",str(n*factor),f"Multiply {n} by {factor} to get {n*factor}.")

def place_value(grade,rng):
    maxn=99 if grade<=1 else 9999 if grade<=3 else 999999
    n=rng.randint(10,maxn); s=str(n); idx=rng.randrange(len(s)); digit=s[idx]; place=10**(len(s)-idx-1)
    return item(f"In {n:,}, what is the value of the digit {digit}?",str(int(digit)*place),
                f"The digit is in the {place:,}s place.")

def comparison(grade,rng):
    top=20 if grade<=1 else 1000; a,b=rng.randint(0,top),rng.randint(0,top)
    sym=">" if a>b else "<" if a<b else "="
    return item(f"Choose <, >, or = : {a} ___ {b}",sym,f"{a} {sym} {b}.")

def patterns(grade,rng):
    step=rng.randint(1,5 if grade<=2 else 12); start=rng.randint(0,20)
    seq=[start+i*step for i in range(4)]; ans=start+4*step
    return item(f"What comes next? {', '.join(map(str,seq))}, ___",str(ans),
                f"The rule is +{step}, so the next number is {ans}.")

def word_problem(grade,difficulty,rng,constraints=None):
    constraints=constraints or {}
    if constraints.get("two_step"):
        groups=rng.randint(2,8); each=rng.randint(2,10); added=rng.randint(1,20)
        total=groups*each+added
        return item(f"There are {groups} boxes with {each} pencils in each box. Then {added} more pencils are added. How many pencils are there altogether?",
                    str(total),
                    f"First multiply {groups} × {each} = {groups*each}. Then add {added}: {groups*each} + {added} = {total}.",
                    kind="response")
    topic=rng.choice(["addition","subtraction"]+(["multiplication","division"] if grade>=3 else []))
    x=arithmetic(topic,grade,difficulty,None,rng); nums=[int(v) for v in re.findall(r"\d+",x["prompt"])]
    name=rng.choice(("Maya","Rose","Jordan","Kai","Luna"))
    if topic=="addition": p=f"{name} has {nums[0]} stickers and gets {nums[1]} more. How many now?"
    elif topic=="subtraction": p=f"{name} has {nums[0]} apples and gives away {nums[1]}. How many remain?"
    elif topic=="multiplication": p=f"There are {nums[0]} boxes with {nums[1]} pencils each. How many pencils altogether?"
    else: p=f"{nums[0]} crackers are shared equally among {nums[1]} children. How many each?"
    x["prompt"]=p; x["kind"]="response"; x["lines"]=2; return x

def build(spec,rng):
    t,g,d=spec["topic"],spec["grade"],spec["difficulty"]
    constraints=spec.get("constraints") or {}
    if t=="multiplication" and constraints.get("equal_groups"):
        groups=rng.randint(2,10); each=rng.randint(2,10)
        return item(f"There are {groups} equal groups with {each} objects in each group. How many objects altogether?",
                    str(groups*each),f"{groups} groups of {each} is {groups} × {each} = {groups*each}.",kind="response")
    if t=="division" and constraints.get("sharing_grouping"):
        groups=rng.randint(2,10); each=rng.randint(2,10); total=groups*each
        return item(f"{total} objects are shared equally among {groups} groups. How many objects are in each group?",
                    str(each),f"{total} ÷ {groups} = {each}; each group receives {each}.",kind="response")
    if t in {"addition","subtraction","multiplication","division","mixed"}: return arithmetic(t,g,d,spec["within"],rng)
    if t=="fractions": return fractions(g,d,rng,constraints)
    if t=="decimals": return decimals(g,rng)
    if t=="percent": return percent(rng)
    if t=="algebra": return algebra(g,d,rng)
    if t=="geometry": return geometry(g,rng)
    if t=="time": return time_problem(rng,constraints)
    if t=="money": return money(rng,constraints)
    if t=="measurement": return measurement(rng)
    if t=="place-value": return place_value(g,rng)
    if t=="comparison": return comparison(g,rng)
    if t=="patterns": return patterns(g,rng)
    return word_problem(g,d,rng,constraints)

def generate_math(payload:dict[str,Any],rng:Random):
    spec=infer_spec(payload); out=[]; seen=set(); tries=0
    while len(out)<spec["count"] and tries<spec["count"]*30:
        tries+=1; x=format_question(build(spec,rng),spec["question_type"],rng)
        key=(x["prompt"],x["answer"])
        if key in seen: continue
        seen.add(key); out.append(x)
    if len(out)<spec["count"]: raise ValueError("could not generate enough distinct math problems")
    return spec,out
