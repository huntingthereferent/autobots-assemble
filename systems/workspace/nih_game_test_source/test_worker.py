"""Bounded temporal-game test worker: analyze ACTUAL browser-to-Python events.

No test receives credit merely because the game, adapter, or previous worker
is COMPLETE. Original browser query events must demonstrate a change in what
was knowable while target validity remains fixed.
"""
import hashlib,json,os,sys

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def compute(data):
    if type(data) is not dict or set(data)!={
        "kind","synthetic","parent_jobs","browser","events","cutover_turn",
        "target_at","known_at_before","known_at_after","prototype_sha256"}:
        raise ValueError("exact live temporal game-test evidence required")
    if data["kind"]!="native-game-backed-temporal-test/v1" or data["synthetic"] is not True:
        raise ValueError("only verified synthetic source results supported")
    if data["parent_jobs"]!=[
        "nih-packet-001","nih-prototype-001",
        "game-worker-ready-joined-001","live-game-temporal-001"]:
        raise ValueError("native source-owned test parents changed")
    browser=data["browser"]
    if (type(browser) is not dict or
            browser.get("kind")!="game-temporal-live-browser-witness/v1" or
            browser.get("game_solved") is not True or
            browser.get("future_leakage_detected") is not True or
            browser.get("original_prototype_job")!="nih-prototype-001" or
            browser.get("original_game_job")!="build-game-room-v1"):
        raise ValueError("independent original Chromium WITNESS absent")
    rows=data["events"]
    if type(rows) is not list or not 4<=len(rows)<=60:
        raise ValueError("actual browser temporal queries absent or out of bounds")
    cut=data["cutover_turn"]
    if type(cut) is not int or not 1<=cut<=20:
        raise ValueError("game cutover turn invalid")
    before=after=0
    prev=-1
    queries=[]
    for row in rows:
        if type(row) is not dict or set(row)!={"turn","request","result"}:
            raise ValueError("one logged source query differs")
        turn=row["turn"];request=row["request"];res=row["result"]
        if type(turn) is not int or not 0<=turn<=100 or turn<prev:
            raise ValueError("nonmonotonic game turn in browser query history")
        prev=turn
        expected_known=data["known_at_after"] if turn>=cut else data["known_at_before"]
        if (type(request) is not dict or set(request)!={"known_at","target_at"} or
                request!={"known_at":expected_known,"target_at":data["target_at"]} or
                res.get("known_at")!=expected_known or
                res.get("target_at")!=data["target_at"] or
                res.get("prototype_sha256")!=data["prototype_sha256"]):
            raise ValueError("game query did not come from original temporal Python")
        temporal=res["temporal_ids"];static=res["static_snapshot_ids"]
        withheld=res["future_leakage_ids"]
        if (type(temporal) is not list or type(static) is not list or
                type(withheld) is not list or
                sorted(set(temporal+withheld))!=static or
                set(temporal).intersection(withheld)):
            raise ValueError("temporal and static source evidence disagree")
        if turn<cut:
            before+=1
            if "delayed-result" not in withheld:
                raise ValueError("game revealed future evidence before it was knowable")
        else:
            after+=1
            if ("delayed-result" not in temporal or
                    "delayed-result" in withheld):
                raise ValueError("game failed to reveal newly knowable event")
        queries.append((turn,request["known_at"],request["target_at"],
                        tuple(temporal),tuple(withheld)))
    if before<1 or after<1:
        raise ValueError("not a before/after temporal game experiment")
    if browser.get("live_queries")!=len(rows) or browser.get("game_actions")<cut:
        raise ValueError("browser independent game action/query witness differs")
    return {"kind":"native-temporal-game-test-result/v1",
            "query_history_sha256":hashlib.sha256(canonical(rows).encode()).hexdigest(),
            "query_count":len(rows),"before_cutover_queries":before,
            "after_cutover_queries":after,"cutover_turn":cut,
            "original_temporal_source_sha256":data["prototype_sha256"],
            "actual_browser_source":"GAME_TEMPORAL_LIVE_BROWSER_RETURNED",
            "static_snapshot_leakage_detected":True,
            "independent_python_replay_required":True,
            "verified_synthetic_timing_only":True,
            "clinical_verdict":"NOT_EVALUATED",
            "official_nih_submission":False}

if __name__=="__main__":
    try:
        raw=sys.stdin.read(160001)
        if len(raw)>160000:raise ValueError("bounded game-backed temporal test too large")
        print(json.dumps({"report":compute(json.loads(raw)),"pid":os.getpid()},sort_keys=True))
    except (ValueError,TypeError,KeyError) as exc:
        print(str(exc),file=sys.stderr)
        raise SystemExit(2)
