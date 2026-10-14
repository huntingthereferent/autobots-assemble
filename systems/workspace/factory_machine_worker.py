"""Explicitly simulated Factory machine-stage worker source.

Copied into a workstation edition and executed in a local child process.
The source-owned Factory simulator, not this copy, decides whether output
may be admitted. This is NOT a physical machine or hardware interface.
"""
from __future__ import annotations

import json
import os
import sys


def simulate(inputs: dict) -> dict:
    if (not isinstance(inputs, dict) or
            not isinstance(inputs.get('product'), str) or
            not inputs['product'] or
            type(inputs.get('quantity')) is not int or
            inputs['quantity'] <= 0 or
            inputs.get('material_state') != 'received'):
        raise ValueError('Factory machine simulation requires received material and valid product/quantity')
    return {'part': inputs['product'] + '-part',
            'quantity': inputs['quantity'],
            'part_state': 'machined'}


if __name__ == '__main__':
    payload = json.load(sys.stdin)
    print(json.dumps({'output': simulate(payload), 'child_pid': os.getpid()}))
