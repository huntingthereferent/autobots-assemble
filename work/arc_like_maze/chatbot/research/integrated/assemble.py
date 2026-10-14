#!/usr/bin/env python3
"""Build exact historical flat CP20–CP30 source from immutable staged inputs."""
import argparse, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def reconstruct(stage, destination):
    m=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    if type(stage) is not int or not (20 <= stage <= 30):
        raise ValueError('stage must be 20 through 30')
    dest=Path(destination)
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError(f'refusing to overwrite nonempty destination: {dest}')
    selected={n:item for n,item in m['files'].items() if item['stage']<=stage}
    expected=201+8*(stage-20)
    if len(selected)!=expected:
        raise ValueError(f'expected {expected} original source files; found {len(selected)}')
    payloads={}
    for name,item in selected.items():
        if Path(name).name!=name or Path(name).is_absolute():
            raise ValueError(f'unsafe original filename: {name}')
        source=(ROOT/item['path'])
        raw=source.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['sha256'] or len(raw)!=item['size']:
            raise ValueError(f'original source altered or absent: {name}')
        payloads[name]=raw
    dest.mkdir(parents=True,exist_ok=True)
    for name,raw in payloads.items():
        (dest/name).write_bytes(raw)
    print(f'CP-{stage}: restored {len(payloads)} original files to {dest}')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',type=int,default=30)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();reconstruct(a.stage,a.out)
