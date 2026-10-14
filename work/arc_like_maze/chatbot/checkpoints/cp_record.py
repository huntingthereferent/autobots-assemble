"""Deterministic checkpoint -> finite correspondence research views.

Stdlib only. Does not create, authenticate, or publish checkpoint evidence.
Invoked by the research harness when it has already completed a checkpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

BEGIN = '<!-- CHATBOT-CP-LEDGER:BEGIN -->'
END = '<!-- CHATBOT-CP-LEDGER:END -->'
NAME = re.compile(r'CP-(\d{4})\.json\Z')
SHA = re.compile(r'[a-f0-9]{64}\Z')
MARKDOWN_LINK = re.compile(r'[A-Za-z0-9][A-Za-z0-9_./-]*\Z')
STATUSES = {'witnessed', 'partial', 'blocked'}
FIELDS = {'cp', 'date', 'title', 'status', 'summary', 'observation', 'preserved',
          'boundary', 'next', 'record', 'source', 'tests_path', 'tests', 'archive', 'reproduction'}


class CheckpointError(ValueError):
    pass


def plain(value, field, limit=500):
    if not isinstance(value, str) or not value or len(value) > limit or any(x in value for x in '<>|\r\n'):
        raise CheckpointError(f'invalid public text: {field}')
    return value


def safe_name(s, field):
    if not isinstance(s, str) or not MARKDOWN_LINK.fullmatch(s) or s.startswith('/') or '..' in s.split('/') or s.startswith('.'):
        raise CheckpointError(f'invalid file path: {field}')
    return s


def validate(m):
    if not isinstance(m, dict) or set(m) != FIELDS:
        raise CheckpointError('checkpoint keys must match documented schema exactly')
    if type(m['cp']) is not int or not 1 <= m['cp'] <= 9999:
        raise CheckpointError('invalid checkpoint number')
    try:
        if date.fromisoformat(m['date']).isoformat() != m['date']:
            raise ValueError('date normalization')
    except (ValueError, TypeError) as e:
        raise CheckpointError('invalid ISO date') from e
    if m['status'] not in STATUSES:
        raise CheckpointError('invalid checkpoint status')
    for key in ('title', 'summary', 'observation', 'preserved', 'boundary', 'next'):
        plain(m[key], key, 120 if key == 'title' else 500)
    for key in ('record', 'source', 'tests_path'):
        safe_name(m[key], key)
    t=m['tests']
    if not isinstance(t, dict) or set(t)!={'passed','executed','scope'} or type(t['passed']) is not int or type(t['executed']) is not int or not 0 <= t['passed'] <= t['executed'] <= 1000000 or t['scope'] not in ('targeted', 'historical-full', 'not-run'):
        raise CheckpointError('invalid test accounting')
    if t['scope']=='not-run' and (t['passed'] or t['executed']):
        raise CheckpointError('not-run cannot report tests')
    a=m['archive']
    if not isinstance(a, dict) or set(a)!={'name','sha256','files','availability'}:
        raise CheckpointError('invalid archive fields')
    safe_name(a['name'], 'archive.name')
    if not a['name'].endswith('.zip') or not SHA.fullmatch(a['sha256']):
        raise CheckpointError('invalid archive name/hash')
    if type(a['files']) is not int or not 1<=a['files']<=1000000:
        raise CheckpointError('invalid archive file count')
    if a['availability'] not in ('conversation-local', 'repository', 'release'):
        raise CheckpointError('invalid archive availability')
    r=m['reproduction']
    if not isinstance(r, list) or not 1 <= len(r)<=12:
        raise CheckpointError('reproduction commands required')
    for i,c in enumerate(r):
        plain(c, f'reproduction[{i}]', 200)
        if '`' in c:
            raise CheckpointError('commands may not contain markdown backticks')
    return m


def encode(m):
    validate(m)
    return json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True)+'\n'


def entries(root):
    loc=root/'checkpoints'
    found=[]
    for file in sorted(loc.glob('CP-*.json')):
        match=NAME.fullmatch(file.name)
        if not match:
            raise CheckpointError(f'unrecognized CP file name: {file.name}')
        m=validate(json.loads(file.read_text(encoding='utf-8')))
        if int(match.group(1))!=m['cp']:
            raise CheckpointError('manifest ID and filename disagree')
        found.append(m)
    if len({m['cp'] for m in found})!=len(found):
        raise CheckpointError('duplicate CP identifiers')
    if found and [m['cp'] for m in found]!=list(range(found[0]['cp'],found[-1]['cp']+1)):
        raise CheckpointError('CP sequence has a gap')
    return found


def short(m):
    t=m['tests']
    return f"{t['passed']}/{t['executed']} ({t['scope']})"


def about(ms):
    if not ms:
        raise CheckpointError('at least one checkpoint required')
    last=ms[-1]
    lines=[
        '# Finite Correspondence Research — About Me', '',
        'This page belongs to the **finite correspondence research checkpoint harness**, not to the researcher’s personal profile. A chatbot is one possible application, not the name of this research.', '',
        'The research follows relations admitted by witnessed finite transitions and exact source conditions. Changes may come from surrounding systems and are checked when invoked; independent goals or continuous monitoring are not required.', '',
        '## Current checkpoint', '',
        f"**CP-{last['cp']:04d} · {last['title']}** · {last['date']} · {last['status']}", '',
        last['summary'], '',
        f"**Observed:** {last['observation']}", '',
        f"**Preserved:** {last['preserved']}", '',
        f"**Boundary:** {last['boundary']}", '',
        f"**Verification record:** {short(last)}. Local test execution is distinct from GitHub CI and from independent reproduction.", '',
        f"**Next possible movement:** {last['next']}", '',
        '## Recent checkpoints', '',
        '| CP | Change | Evidence |', '| --- | --- | --- |'
    ]
    for m in reversed(ms[-5:]):
        lines.append(f"| [CP-{m['cp']:04d}](checkpoints/CP-{m['cp']:04d}.json) | {m['title']} | [{m['record']}]({m['record']}) |")
    lines += ['', '## Follow the record', '',
              '[Provenance and full checkpoint ledger](PROVENANCE.md) · [Research index](README.md) · [Checkpoint handoff contract](checkpoints/HARNESS.md)', '',
              '<!-- Generated by checkpoints/cp_record.py from witnessed CP manifests. Do not hand-edit; submit a new CP for new observations. -->', '']
    return '\n'.join(lines)


def ledger(ms):
    lines=[BEGIN, '## Checkpoint output ledger (harness-maintained)', '',
           'Each row is derived from an explicit CP manifest. The record links are repository evidence indexes; archive filenames below are identifiers, not download links. A CP manifest is not, by itself, independent verification of its claims.', '',
           '| CP | Observed movement | Survives | Verification | Archive |',
           '| --- | --- | --- | --- | --- |']
    for m in ms:
        a=m['archive']
        lines.append(f"| [CP-{m['cp']:04d}](checkpoints/CP-{m['cp']:04d}.json) · {m['date']} | **{m['title']}** — {m['summary']} | {m['preserved']} | {short(m)}; [{m['record']}]({m['record']}) | `{a['name']}` · {a['files']} files · {a['availability']} |")
    lines.extend(['', '### Latest checkpoint reproduction', ''])
    for cmd in ms[-1]['reproduction']:
        lines.append(f'- `{cmd}`')
    lines += ['',f"Latest archive SHA-256: `{ms[-1]['archive']['sha256']}`",'', END]
    return '\n'.join(lines)


def provenance(old, ms):
    generated=ledger(ms)
    if BEGIN in old or END in old:
        if old.count(BEGIN)!=1 or old.count(END)!=1 or old.index(BEGIN)>old.index(END):
            raise CheckpointError('corrupted provenance marker pair')
        return old[:old.index(BEGIN)]+generated+old[old.index(END)+len(END):]
    return old.rstrip()+'\n\n'+generated+'\n'


def render(root):
    ms=entries(root)
    path=root/'PROVENANCE.md'
    if not path.is_file():
        raise CheckpointError('existing PROVENANCE.md required; never recreate prior history')
    return about(ms),provenance(path.read_text(encoding='utf-8'), ms)


def sync(root):
    a,p=render(root)
    (root/'ABOUT_ME.md').write_text(a, encoding='utf-8')
    (root/'PROVENANCE.md').write_text(p, encoding='utf-8')


def check(root):
    a,p=render(root)
    if not (root/'ABOUT_ME.md').is_file() or (root/'ABOUT_ME.md').read_text(encoding='utf-8')!=a:
        raise CheckpointError('ABOUT_ME.md out of sync; checkpoint output was omitted or changed')
    if (root/'PROVENANCE.md').read_text(encoding='utf-8')!=p:
        raise CheckpointError('PROVENANCE.md out of sync; checkpoint output was omitted or changed')
    return len(entries(root))


def record(root, input_path):
    m=validate(json.loads(Path(input_path).read_text(encoding='utf-8')))
    ms=entries(root)
    highest=ms[-1]['cp'] if ms else m['cp']-1
    target=root/'checkpoints'/f"CP-{m['cp']:04d}.json"
    payload=encode(m)
    if m['cp'] == highest and ms[-1] == m:
        check(root)
        return 'already-recorded'
    if m['cp'] != highest+1 or target.exists():
        raise CheckpointError('cannot overwrite, skip, or reorder a recorded checkpoint')
    if not (root/'PROVENANCE.md').is_file():
        raise CheckpointError('missing existing provenance')
    # Render all three results without modifying the repository yet.
    prior_prov=(root/'PROVENANCE.md').read_text(encoding='utf-8')
    new_ms=ms+[m]
    a=about(new_ms)
    p=provenance(prior_prov,new_ms)
    target.write_text(payload,encoding='utf-8')
    (root/'ABOUT_ME.md').write_text(a,encoding='utf-8')
    (root/'PROVENANCE.md').write_text(p,encoding='utf-8')
    return 'recorded'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('check','sync','record'))
    parser.add_argument('input',nargs='?',help='new CP manifest for record')
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent)
    args=parser.parse_args(argv)
    try:
        if args.command=='check':
            print(f'{check(args.root)} checkpoint(s) consistent')
        elif args.command=='sync':
            sync(args.root);print('About Me and provenance synced')
        elif args.input:
            print(record(args.root,args.input))
        else:
            parser.error('record requires a manifest path')
        return 0
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(f'CP_WALL: {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
