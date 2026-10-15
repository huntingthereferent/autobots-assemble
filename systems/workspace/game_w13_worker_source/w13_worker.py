"""Explicit standalone source-edition W13 engine worker; JSON stdin -> stdout."""
import json
import os
import sys
from w13_engine import play


def main():
    req=json.load(sys.stdin)
    if not isinstance(req,dict) or set(req)!={'contract','worlds','actions'} or req['contract']!='game-w13-multiworld-v1':
        raise ValueError('invalid W13 input contract')
    result=play(req['worlds'],req['actions'])
    print(json.dumps({'report':result,'pid':os.getpid()},sort_keys=True,separators=(',',':')))

if __name__=='__main__':main()