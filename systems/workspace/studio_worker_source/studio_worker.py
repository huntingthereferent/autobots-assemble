"""Independent source-owned A/B Studio finite render worker. No network or Suno dependencies.

This implementation is intentionally standalone from studio_native.py. The host
replays the output separately before any native COMPLETE can be accepted.
"""
import hashlib
import json
import math
import os
import struct
import sys

TICKS=960
def rounded(n,d):
    return (n+d//2)//d if n>=0 else -((-n+d//2)//d)

def frames_for(tick,rate,bpm):
    return rounded(tick*rate*60,bpm*TICKS)

def render(req):
    if not isinstance(req,dict) or set(req)!={"schema","sample_rate","bpm","duration_ticks","sources","tracks"} or req["schema"]!="ab-studio-render/v1":
        raise ValueError("request contract")
    rate,bpm,length=req["sample_rate"],req["bpm"],req["duration_ticks"]
    if any(type(n)!=int for n in (rate,bpm,length)) or not 8000<=rate<=48000 or not 40<=bpm<=240 or not 1<=length<=7680 or frames_for(length,rate,bpm)>12000:
        raise ValueError("finite time/rate")
    if type(req["sources"]) is not list or len(req["sources"])>4 or type(req["tracks"]) is not list or not 1<=len(req["tracks"])<=8:
        raise ValueError("source/track budget")
    sources={}
    for s in req["sources"]:
        if type(s)!=dict or set(s)!={"id","sha256","pcm"} or not isinstance(s["id"],str) or not 1<=len(s["id"])<=40 or s["id"] in sources or type(s["pcm"])!=list or not 1<=len(s["pcm"])<=8192:
            raise ValueError("source shape")
        if any(type(v)!=int or not -32768<=v<=32767 for v in s["pcm"]):
            raise ValueError("PCM16")
        digest=hashlib.sha256(struct.pack("<"+"h"*len(s["pcm"]),*s["pcm"])).hexdigest()
        if s["sha256"]!=digest:
            raise ValueError("source identity mismatch")
        sources[s["id"]]=s["pcm"]
    samples=frames_for(length,rate,bpm)
    left=[0]*samples
    right=[0]*samples
    solo=any(t.get("solo") is True for t in req["tracks"])
    seen_tracks=set()
    for track in req["tracks"]:
        if type(track)!=dict or set(track)!={"id","gain","pan","mute","solo","automation","clips"}:
            raise ValueError("track fields")
        ident=track["id"]
        if not isinstance(ident,str) or not 1<=len(ident)<=40 or ident in seen_tracks:
            raise ValueError("track id")
        seen_tracks.add(ident)
        if any(type(track[k])!=int for k in ("gain","pan")) or not 0<=track["gain"]<=1500 or not -1000<=track["pan"]<=1000 or any(type(track[k])!=bool for k in ("mute","solo")):
            raise ValueError("mix controls")
        automation=track["automation"]
        clips=track["clips"]
        if type(automation)!=list or len(automation)>32 or type(clips)!=list or len(clips)>16:
            raise ValueError("automation/clip budget")
        previous=-1
        for p in automation:
            if type(p)!=dict or set(p)!={"tick","gain"} or type(p["tick"])!=int or type(p["gain"])!=int or not previous<p["tick"]<=length or not 0<=p["gain"]<=1500:
                raise ValueError("automation points")
            previous=p["tick"]
        signal=[0]*samples
        for clip in clips:
            if type(clip)!=dict or "kind" not in clip:
                raise ValueError("clip")
            if clip["kind"]=="audio":
                if set(clip)!={"kind","id","source","start","length","offset","rate_num","rate_den"}:
                    raise ValueError("audio clip")
                if clip["source"] not in sources or any(type(clip[k])!=int for k in ("start","length","offset","rate_num","rate_den")) or not 0<=clip["start"]<length or not 1<=clip["length"]<=length-clip["start"] or not 0<=clip["offset"]<=8192 or not 1<=clip["rate_num"]<=4 or not 1<=clip["rate_den"]<=4:
                    raise ValueError("audio clip range")
                data=sources[clip["source"]]
                a,b=frames_for(clip["start"],rate,bpm),min(samples,frames_for(clip["start"]+clip["length"],rate,bpm))
                for i in range(a,b):
                    index_n=(i-a)*clip["rate_num"]
                    pos=clip["offset"]+index_n//clip["rate_den"]
                    if pos>=len(data):continue
                    fraction=index_n%clip["rate_den"]
                    v=data[pos]
                    neighbor=data[pos+1] if pos+1<len(data) else 0
                    signal[i]+=rounded(v*(clip["rate_den"]-fraction)+neighbor*fraction,clip["rate_den"])
            elif clip["kind"]=="midi":
                if set(clip)!={"kind","id","start","length","notes"} or any(type(clip[k])!=int for k in ("start","length")) or not 0<=clip["start"]<length or not 1<=clip["length"]<=length-clip["start"] or type(clip["notes"])!=list or len(clip["notes"])>64:
                    raise ValueError("MIDI clip range")
                for n in clip["notes"]:
                    if type(n)!=dict or set(n)!={"pitch","start","length","velocity"} or any(type(n[k])!=int for k in n) or not 36<=n["pitch"]<=84 or not 0<=n["start"]<clip["length"] or not 1<=n["length"]<=clip["length"]-n["start"] or not 1<=n["velocity"]<=127:
                        raise ValueError("MIDI note")
                    n0=frames_for(clip["start"]+n["start"],rate,bpm)
                    n1=min(samples,frames_for(clip["start"]+n["start"]+n["length"],rate,bpm))
                    freq=440.0*2.0**((n["pitch"]-69)/12)
                    for i in range(n0,n1):
                        signal[i]+=round(12000*n["velocity"]/127*math.sin(2*math.pi*freq*(i-n0)/rate))
            else:
                raise ValueError("unsupported clip kind")
        if track["mute"] or (solo and not track["solo"]):
            continue
        points=[(0,track["gain"])]+[(frames_for(p["tick"],rate,bpm),p["gain"]) for p in automation]
        k=0
        for i,s in enumerate(signal):
            while k+1<len(points) and i>=points[k+1][0]:
                k+=1
            if k+1<len(points):
                f0,v0=points[k];f1,v1=points[k+1]
                gain=v0 if f1<=f0 else v0+rounded((v1-v0)*(i-f0),f1-f0)
            else:
                gain=points[k][1]
            left[i]+=rounded(s*gain*(1000-track["pan"]),2000000)
            right[i]+=rounded(s*gain*(1000+track["pan"]),2000000)
    l=[max(-32768,min(32767,x)) for x in left]
    r=[max(-32768,min(32767,x)) for x in right]
    frames=struct.pack("<"+"h"*(2*samples),*(v for pair in zip(l,r) for v in pair))
    return {"schema":"ab-studio-render-result/v1","sample_rate":rate,"frames":samples,
            "left":l,"right":r,"pcm_sha256":hashlib.sha256(frames).hexdigest()}

if __name__=="__main__":
    request=json.load(sys.stdin)
    print(json.dumps({"result":render(request),"pid":os.getpid()},separators=(",",":")))
