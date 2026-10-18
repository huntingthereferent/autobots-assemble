"""A SECOND bounded W13 WITNESS worker. Independent finite replay in copied source.

Computes its own expected steps from declared W13 rooms and the parent's
source-owned receipt. The host separately replays the original byte-pinned W12.
No game authority derives from a displayed receipt or a completed CI check.
"""
import hashlib,json,os,sys

def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False)

def verify(inputs):
    if type(inputs) is not dict or set(inputs)!={"request","receipt","parent_job_id"}:
        raise ValueError("bounded native game witness requires exact W13 parent")
    request=inputs["request"]; receipt=inputs["receipt"]
    if (inputs["parent_job_id"]!="game-w13-cp-joined-001" or
            request["contract"]!="game-w13-multiworld-v1" or
            request["actions"]!=["right","interact","advance","right","interact"] or
            receipt["version"]!="game-w13-multiworld-v1" or
            receipt["actions"]!=request["actions"]):
        raise ValueError("game W13 parent contract mismatch")
    if type(request["worlds"]) is not list or len(request["worlds"])!=2:
        raise ValueError("W13 is exactly two worlds")
    worlds=request["worlds"]
    if [w["id"] for w in worlds]!=["first-room","second-room"]:
        raise ValueError("W13 world identities changed")
    states=[{"x":w["spec"]["start"][0],"y":w["spec"]["start"][1],
             "collected":False,"turns":0} for w in worlds]
    actual_actions=[[],[]];observations=[[],[]];crossings=[];world=0
    for action in request["actions"]:
        if action=="advance":
            if world!=0 or not states[0]["collected"]:
                raise ValueError("cannot advance before collecting")
            crossings.append({
                "action":"advance","from_world":worlds[0]["id"],
                "to_world":worlds[1]["id"],
                "before":{"world_id":worlds[0]["id"],"state":dict(states[0])},
                "after":{"world_id":worlds[1]["id"],"state":dict(states[1])}})
            world=1
            continue
        state=states[world]
        before=dict(state)
        if action=="right":
            if state["x"]+1<worlds[world]["spec"]["width"]:
                state["x"]+=1;verdict="moved"
            else:
                verdict="blocked-by-boundary"
        elif action=="interact":
            target=worlds[world]["spec"]["target"]
            if state["collected"]:
                verdict="already-collected"
            elif abs(target[0]-state["x"])+abs(target[1]-state["y"])==1:
                state["collected"]=True;verdict="collected"
            else:verdict="out-of-reach"
        else:raise ValueError("unrecognized declared W13 action")
        state["turns"]+=1
        actual_actions[world].append(action)
        observations[world].append({"action":action,"before":before,
                                    "after":dict(state),"verdict":verdict})
    if len(crossings)!=1 or not all(x["collected"] for x in states):
        raise ValueError("W13 world transition incomplete")
    for index,w in enumerate(worlds):
        original=receipt["worlds"][index]
        if (original["id"]!=w["id"] or original["spec"]!=w["spec"] or
                original["actions"]!=actual_actions[index] or
                canonical(original["observations"])!=canonical(observations[index]) or
                canonical(original["final"])!=canonical(states[index])):
            raise ValueError("independent game steps do not match source-owned receipt")
    if (canonical(receipt["boundaries"])!=canonical(crossings)
            or canonical(receipt["final"])!=canonical({
                "world_id":worlds[1]["id"],"state":states[1],
                "worlds_completed":2,"solved":True})):
        raise ValueError("game cross-world or final state differs")
    # Explicit independent NEGATIVE: adding an early advance must be rejected.
    if states[0]["turns"]!=2 or states[1]["turns"]!=2:
        raise ValueError("unexpected source turn accounting")
    before=({"x":worlds[0]["spec"]["start"][0],"y":worlds[0]["spec"]["start"][1],
             "collected":False,"turns":0})
    if before["collected"]:
        raise ValueError("invalid first-room negative precondition")
    return {"kind":"w13-independent-native-game-verdict/v1",
            "worlds_completed":2,"cross_world_boundaries":len(crossings),
            "per_world_turns":[states[0]["turns"],states[1]["turns"]],
            "negative_early_advance_rejected":True,
            "receipt_sha256":hashlib.sha256(canonical(receipt).encode()).hexdigest(),
            "w12_sha256":request["w12_sha256"]}

if __name__=="__main__":
    try:
        raw=sys.stdin.read(18001)
        if len(raw)>18000:raise ValueError("source witness input too large")
        print(json.dumps({"result":verify(json.loads(raw)),"pid":os.getpid()},sort_keys=True))
    except (ValueError,KeyError,TypeError,IndexError) as e:
        print(type(e).__name__+": "+str(e),file=sys.stderr)
        raise SystemExit(2)
