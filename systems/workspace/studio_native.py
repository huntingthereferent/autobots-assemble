"""Host-owned Studio renderer contract; separate implementation from copied worker."""
from __future__ import annotations
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import struct
import wave

SCHEMA="ab-studio-render/v1"
RESULT_SCHEMA="ab-studio-render-result/v1"
VERIFIER="workstation:studio-render-native/v1"
WITNESS="host-owned stereo frame-by-frame replay"
SOURCE_LOCATOR="repo:systems/workspace/studio_worker_source/studio_worker.py"
TICKS=960

def rounded(n:int,d:int)->int:
    if d<=0: raise ValueError("invalid divisor")
    return (n+d//2)//d if n>=0 else -((-n+d//2)//d)

def tick_frame(tick,rate,bpm):
    return rounded(tick*rate*60,bpm*TICKS)

def pcm_hash(frames:list[int])->str:
    return sha256(struct.pack("<"+"h"*len(frames),*frames)).hexdigest()

def validate_input(row:object)->dict:
    if type(row)!=dict or set(row)!={"schema","sample_rate","bpm","duration_ticks","sources","tracks"} or row["schema"]!=SCHEMA:
        raise ValueError("Studio request shape")
    rate,bpm,duration=row["sample_rate"],row["bpm"],row["duration_ticks"]
    if any(type(n)!=int for n in (rate,bpm,duration)) or not 8000<=rate<=48000 or not 40<=bpm<=240 or not 1<=duration<=7680 or tick_frame(duration,rate,bpm)>12000:
        raise ValueError("Studio finite duration or rate")
    tracks,sources=row["tracks"],row["sources"]
    if type(sources)!=list or len(sources)>4 or type(tracks)!=list or not 1<=len(tracks)<=8:
        raise ValueError("Studio source/track bounds")
    source_ids=set()
    for source in sources:
        if type(source)!=dict or set(source)!={"id","sha256","pcm"} or not isinstance(source["id"],str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}",source["id"]) or source["id"] in source_ids:
            raise ValueError("Studio source id")
        source_ids.add(source["id"])
        pcm=source["pcm"]
        if type(pcm)!=list or not 1<=len(pcm)<=8192 or any(type(n)!=int or not -32768<=n<=32767 for n in pcm) or source["sha256"]!=pcm_hash(pcm):
            raise ValueError("invalid PCM or digest")
    track_ids=set();clip_ids=set()
    for track in tracks:
        if type(track)!=dict or set(track)!={"id","gain","pan","mute","solo","automation","clips"}:
            raise ValueError("Studio track shape")
        if not isinstance(track["id"],str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}",track["id"]) or track["id"] in track_ids:
            raise ValueError("track id")
        track_ids.add(track["id"])
        if (type(track["gain"])!=int or not 0<=track["gain"]<=1500
                or type(track["pan"])!=int or not -1000<=track["pan"]<=1000
                or type(track["mute"])!=bool or type(track["solo"])!=bool):
            raise ValueError("mixer control")
        autom,clips=track["automation"],track["clips"]
        if type(autom)!=list or len(autom)>32 or type(clips)!=list or len(clips)>16:
            raise ValueError("Studio lane bounds")
        previous=-1
        for point in autom:
            if type(point)!=dict or set(point)!={"tick","gain"} or type(point["tick"])!=int or type(point["gain"])!=int or not previous<point["tick"]<=duration or not 0<=point["gain"]<=1500:
                raise ValueError("automation point")
            previous=point["tick"]
        for clip in clips:
            if type(clip)!=dict or clip.get("kind") not in ("audio","midi"):
                raise ValueError("clip kind")
            kind=clip["kind"]
            fields={"kind","id","start","length","source","offset","rate_num","rate_den"} if kind=="audio" else {"kind","id","start","length","notes"}
            if set(clip)!=fields or not isinstance(clip["id"],str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}",clip["id"]) or clip["id"] in clip_ids:
                raise ValueError("clip identity/fields")
            clip_ids.add(clip["id"])
            if type(clip["start"])!=int or type(clip["length"])!=int or not 0<=clip["start"]<duration or not 1<=clip["length"]<=duration-clip["start"]:
                raise ValueError("clip time")
            if kind=="audio":
                if clip["source"] not in source_ids or any(type(clip[k])!=int for k in ("offset","rate_num","rate_den")) or not 0<=clip["offset"]<=8192 or not 1<=clip["rate_num"]<=4 or not 1<=clip["rate_den"]<=4:
                    raise ValueError("audio clip")
            else:
                notes=clip["notes"]
                if type(notes)!=list or len(notes)>64:
                    raise ValueError("MIDI event budget")
                for note in notes:
                    if type(note)!=dict or set(note)!={"pitch","start","length","velocity"} or any(type(v)!=int for v in note.values()):
                        raise ValueError("MIDI note shape")
                    if not 36<=note["pitch"]<=84 or not 0<=note["start"]<clip["length"] or not 1<=note["length"]<=clip["length"]-note["start"] or not 1<=note["velocity"]<=127:
                        raise ValueError("MIDI note range")
    return json.loads(json.dumps(row,sort_keys=True))

def expected_result(raw:object)->dict:
    """Frame-centric host verification; worker is source-centric and uses different loops."""
    request=validate_input(raw)
    sample_rate,bpm,limit=request["sample_rate"],request["bpm"],request["duration_ticks"]
    frames=tick_frame(limit,sample_rate,bpm)
    clips_by_track=[]
    samples={x["id"]:x["pcm"] for x in request["sources"]}
    solo=any(t["solo"] for t in request["tracks"])
    for track in request["tracks"]:
        clips=[]
        for clip in track["clips"]:
            begin=tick_frame(clip["start"],sample_rate,bpm)
            end=tick_frame(clip["start"]+clip["length"],sample_rate,bpm)
            if clip["kind"]=="audio":
                clips.append((clip,begin,end,None))
            else:
                note_regions=[(note,tick_frame(clip["start"]+note["start"],sample_rate,bpm),
                               tick_frame(clip["start"]+note["start"]+note["length"],sample_rate,bpm),
                               440*2**((note["pitch"]-69)/12)) for note in clip["notes"]]
                clips.append((clip,begin,end,note_regions))
        points=[(0,track["gain"])]+[(tick_frame(p["tick"],sample_rate,bpm),p["gain"]) for p in track["automation"]]
        clips_by_track.append((track,clips,points))
    left=[];right=[]
    for frame in range(frames):
        L=R=0
        for track,clips,points in clips_by_track:
            if track["mute"] or (solo and not track["solo"]):continue
            signal=0
            for clip,begin,end,notes in clips:
                if frame<begin or frame>=end: continue
                if clip["kind"]=="audio":
                    src=samples[clip["source"]]
                    distance=frame-begin
                    numerator=distance*clip["rate_num"]
                    index=clip["offset"]+numerator//clip["rate_den"]
                    if index>=len(src):continue
                    sub=numerator%clip["rate_den"]
                    next_value=src[index+1] if index+1<len(src) else 0
                    signal+=rounded(src[index]*(clip["rate_den"]-sub)+next_value*sub,clip["rate_den"])
                else:
                    for note,start,finish,freq in notes:
                        if start<=frame<finish:
                            signal+=round(12000*note["velocity"]/127*math.sin((frame-start)*(math.tau*freq/sample_rate)))
            if not signal:continue
            gain=points[-1][1]
            for k,point in enumerate(points):
                if frame<point[0]:
                    prev=points[k-1]
                    d=point[0]-prev[0]
                    gain=prev[1] if d<=0 else prev[1]+rounded((point[1]-prev[1])*(frame-prev[0]),d)
                    break
                if k==len(points)-1:gain=point[1]
            L+=rounded(signal*gain*(1000-track["pan"]),2000000)
            R+=rounded(signal*gain*(1000+track["pan"]),2000000)
        left.append(max(-32768,min(32767,L)))
        right.append(max(-32768,min(32767,R)))
    packed=struct.pack("<"+"h"*(frames*2),*(n for pair in zip(left,right) for n in pair))
    return {"schema":RESULT_SCHEMA,"sample_rate":sample_rate,"frames":frames,
            "left":left,"right":right,"pcm_sha256":sha256(packed).hexdigest()}

def read_wav_session(file:str|Path)->dict:
    """Local user-selected JSON manifest; WAV sources are never obtained from Suno."""
    filename=Path(file)
    if filename.is_symlink() or not filename.is_file() or filename.stat().st_size>250000:
        raise ValueError("manifest must be an ordinary small file")
    item=json.loads(filename.read_text(encoding="utf8"))
    if type(item)!=dict or set(item)!={"schema","sample_rate","bpm","duration_ticks","sources","tracks"} or item["schema"]!="ab-studio-wav-intake/v1" or type(item["sources"])!=list or len(item["sources"])>4:
        raise ValueError("invalid WAV session manifest")
    raw=[]
    for desc in item["sources"]:
        if type(desc)!=dict or set(desc)!={"id","path"} or not isinstance(desc["path"],str) or not desc["path"].lower().endswith(".wav"):
            raise ValueError("source manifest fields")
        path=(filename.parent/desc["path"]).resolve(strict=True)
        if path.is_symlink() or not path.is_file() or path.stat().st_size>200000:
            raise ValueError("invalid WAV path or size")
        with wave.open(str(path),"rb") as sound:
            if sound.getnchannels()!=1 or sound.getsampwidth()!=2 or sound.getcomptype()!="NONE" or sound.getframerate()!=item["sample_rate"] or not 1<=sound.getnframes()<=8192:
                raise ValueError("WAV must be PCM16 mono with matching rate, max 8192 frames")
            pcm=list(struct.unpack("<"+"h"*sound.getnframes(),sound.readframes(sound.getnframes())))
        raw.append({"id":desc["id"],"sha256":pcm_hash(pcm),"pcm":pcm})
    return validate_input({"schema":SCHEMA,"sample_rate":item["sample_rate"],"bpm":item["bpm"],
                           "duration_ticks":item["duration_ticks"],"sources":raw,"tracks":item["tracks"]})

def write_verified_wav(target:str|Path,render:dict)->dict:
    if type(render)!=dict or render.get("schema")!=RESULT_SCHEMA or type(render.get("left"))!=list or type(render.get("right"))!=list:
        raise ValueError("invalid result")
    n=render["frames"]
    if type(n)!=int or not 1<=n<=12000 or len(render["left"])!=n or len(render["right"])!=n:
        raise ValueError("invalid frame count")
    if any(type(x)!=int or not -32768<=x<=32767 for x in render["left"]+render["right"]):
        raise ValueError("invalid PCM16 output")
    raw=struct.pack("<"+"h"*(2*n),*(v for pair in zip(render["left"],render["right"]) for v in pair))
    if sha256(raw).hexdigest()!=render["pcm_sha256"]:
        raise ValueError("result digest mismatch")
    path=Path(target)
    if path.is_symlink():raise ValueError("output must not be symlink")
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),"wb") as result:
        result.setnchannels(2);result.setsampwidth(2);result.setframerate(render["sample_rate"])
        result.writeframes(raw)
    return {"path":str(path),"sample_rate":render["sample_rate"],"frames":n,"pcm_sha256":render["pcm_sha256"]}
