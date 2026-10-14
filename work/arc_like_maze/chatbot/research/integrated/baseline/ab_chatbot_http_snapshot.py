"""HTTP observation of source-owned finite A/B mathematical versions.

A/B is the language-level referent (see the October 11 Ground Record). This
module ONLY exercises a bounded F3^3 two-generator mathematical example. An
in-process OwnedVersions source exposes immutable revisions over loopback HTTP.
The wire format is not cryptographic attestation, external authentication,
or proof of uninterrupted continuity in a mutable physical system.
"""
from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock, Thread
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import urlopen
import json
import secrets
from typing import Callable

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import Discovery, State
from ab_chatbot_pinned_identity import (
    BoundCorrespondence, IdentityResult, KEYS, OwnedVersions, PinnedView,
    _state, table_digest,
)
from ab_chatbot_stability_witness import TransportedLaw


@dataclass(frozen=True)
class RemoteSnapshot:
    claimed_source: str
    revision: int
    digest: str
    values: tuple[State, ...]

    def step(self, state: State, action: str) -> State:
        if not _state(state) or action not in 'AB':
            raise ValueError('outside F3^3 action domain')
        return self.values[KEYS.index((state, action))]


@dataclass(frozen=True)
class Scan:
    status: str  # OBSERVED_SINGLE_REVISION / MIXED_REVISIONS / UNKNOWN_BUDGET
    revisions: tuple[int, ...]
    calls: int
    detail: str


class SourceOwnedHTTP:
    """Local owner. Mutation is NOT exposed over HTTP; GET is read-only.

    A revision points to a particular PinnedView object issued by OwnedVersions,
    with a complete 54-entry table constructed from an immutable law.
    Lock protects the head/revision selection; captured views never mutate.
    """
    def __init__(self, law: TransportedLaw):
        self._lock = Lock()
        self._versions = OwnedVersions(law)
        self._source_id = secrets.token_hex(16)  # correlation label, NOT a credential
        self.after_capture: Callable[[], None] | None = None  # local test hook

    @property
    def source_id(self) -> str:
        return self._source_id

    def replace(self, law: TransportedLaw) -> PinnedView:
        with self._lock:
            return self._versions.replace(law)

    def select(self, revision: int | None = None) -> PinnedView | None:
        with self._lock:
            if revision is None:
                return self._versions.pin()
            if type(revision) is not int or revision < 0 or revision >= len(self._versions._issued):
                return None
            return self._versions._issued[revision]

    def owned_view(self, snap: RemoteSnapshot) -> PinnedView | None:
        """Trusted same-process evidence, NOT inferable from the HTTP response."""
        if type(snap) is not RemoteSnapshot or snap.claimed_source != self._source_id:
            return None
        view = self.select(snap.revision)
        if view is None or view.digest != snap.digest or view.values != snap.values:
            return None
        self._versions._assert_owned(view)
        return view

    def bind(self, source: FiniteSystem, prior: Discovery, snap: RemoteSnapshot) -> BoundCorrespondence:
        view = self.owned_view(snap)
        if view is None:
            raise ValueError('HTTP snapshot does not match this owner-held historical version')
        return self._versions.bind(source, prior, view)

    def reenter(self, source: FiniteSystem, prior: Discovery, bound: BoundCorrespondence,
                snap: RemoteSnapshot) -> IdentityResult:
        view = self.owned_view(snap)
        if view is None:
            return IdentityResult('UNKNOWN_UNBOUND', 'remote claim does not match the held owner version')
        return self._versions.reenter(source, prior, bound, current=view)


def _int_revision(raw: str) -> int | None:
    if not raw.isascii() or not raw.isdecimal():
        return None
    return int(raw)


class LoopbackHTTP:
    """Actual threaded socket HTTP server for the locally owned model only."""
    def __init__(self, source: SourceOwnedHTTP):
        self.source = source
        self.server: ThreadingHTTPServer | None = None
        self.thread: Thread | None = None

    def __enter__(self):
        source = self.source

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(self, code, data):
                body = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                uri = urlsplit(self.path)
                path, query = uri.path, parse_qs(uri.query)
                if path == '/head':
                    view = source.select()
                    self.reply(200, {'source': source.source_id,
                                     'revision': view.version, 'digest': view.digest})
                    return
                if path in ('/snapshot/current', '/step/live'):
                    view = source.select()
                elif path.startswith('/snapshot/') or path.startswith('/step/'):
                    part = path.split('/')[-1]
                    number = _int_revision(part)
                    if number is None:
                        self.reply(400, {'error': 'invalid revision'})
                        return
                    view = source.select(number)
                else:
                    self.reply(404, {'error': 'route not found'})
                    return
                if view is None:
                    self.reply(404, {'error': 'revision not found'})
                    return
                # Atomically selected before any serialization/callback; old view
                # remains immutable after live head changes.
                hook = source.after_capture
                if hook is not None and path.startswith('/snapshot/'):
                    hook()
                payload = {'source': source.source_id, 'revision': view.version, 'digest': view.digest}
                if path.startswith('/snapshot/'):
                    payload['values'] = [list(s) for s in view.values]
                else:
                    try:
                        raw = query['state'][0].split(',')
                        s = tuple(int(x) for x in raw)
                        act = query['action'][0]
                        if not _state(s) or act not in ('A', 'B'):
                            raise ValueError()
                    except (KeyError, ValueError, IndexError):
                        self.reply(400, {'error': 'invalid state or action'})
                        return
                    payload.update({'state': list(s), 'action': act, 'output': list(view.step(s, act))})
                self.reply(200, payload)

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    @property
    def url(self):
        if self.server is None:
            raise RuntimeError('server not started')
        return 'http://127.0.0.1:' + str(self.server.server_address[1])

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
        if self.thread is not None:
            self.thread.join(timeout=3)


class RemoteObserver:
    """Reads an HTTP response, but cannot authenticate its origin alone."""
    def __init__(self, url: str, timeout: float = 3,
                 *, bound_loopback: LoopbackHTTP | None = None):
        self.url = url.rstrip('/')
        self.timeout = timeout
        self.calls = 0
        # Only an explicitly supplied, active same-process server handle can
        # bind this observer to a local owner. Matching wire metadata is never
        # enough. This is NOT third-party authentication or cryptography.
        if bound_loopback is not None:
            if (type(bound_loopback) is not LoopbackHTTP or
                    bound_loopback.server is None or
                    self.url != bound_loopback.url):
                raise ValueError('bound loopback handle does not own this endpoint')
        self.bound_loopback = bound_loopback

    def request(self, path: str) -> dict:
        self.calls += 1
        with urlopen(self.url + path, timeout=self.timeout) as response:
            data = json.load(response)
        if type(data) is not dict:
            raise ValueError('HTTP result must be an object')
        return data

    def head(self) -> dict:
        raw = self.request('/head')
        if type(raw.get('source')) is not str or type(raw.get('revision')) is not int:
            raise ValueError('invalid head')
        if type(raw.get('digest')) is not str:
            raise ValueError('invalid digest')
        return raw

    @staticmethod
    def decode_snapshot(raw: dict) -> RemoteSnapshot:
        if type(raw) is not dict or type(raw.get('source')) is not str or not raw['source']:
            raise ValueError('missing claimed source identity')
        if type(raw.get('revision')) is not int or raw['revision'] < 0:
            raise ValueError('invalid revision')
        if type(raw.get('values')) is not list:
            raise ValueError('invalid snapshot table')
        values = tuple(tuple(x) if type(x) is list else x for x in raw['values'])
        digest = table_digest(values)  # validates exact labeled domain and shape
        if type(raw.get('digest')) is not str or raw['digest'] != digest:
            raise ValueError('snapshot integrity mismatch')
        return RemoteSnapshot(raw['source'], raw['revision'], digest, values)

    def snapshot(self, revision: int | None = None) -> RemoteSnapshot:
        if revision is not None and (type(revision) is not int or revision < 0):
            raise ValueError('bad revision')
        path = '/snapshot/current' if revision is None else '/snapshot/' + str(revision)
        return self.decode_snapshot(self.request(path))

    def edge(self, state: State, action: str, revision: int | None = None) -> tuple[State, int]:
        if not _state(state) or action not in ('A', 'B'):
            raise ValueError('invalid edge request')
        if revision is not None and (type(revision) is not int or revision < 0):
            raise ValueError('invalid revision')
        rev = 'live' if revision is None else str(revision)
        path = '/step/' + rev + '?' + urlencode({'state': ','.join(map(str, state)), 'action': action})
        raw = self.request(path)
        output = raw.get('output')
        if type(output) is not list or not _state(tuple(output)):
            raise ValueError('invalid output')
        if type(raw.get('revision')) is not int or (revision is not None and raw['revision'] != revision):
            raise ValueError('revision mismatch')
        if raw.get('state') != list(state) or raw.get('action') != action:
            raise ValueError('edge metadata mismatch')
        return tuple(output), raw['revision']

    def live_scan(self, *, budget: int = 54, after: Callable[[int], None] | None = None) -> Scan:
        if type(budget) is not int or budget < 0:
            raise ValueError('invalid budget')
        versions = []
        for i, (state, action) in enumerate(KEYS):
            if i >= budget:
                return Scan('UNKNOWN_BUDGET', tuple(versions), i, 'not all 54 transitions observed')
            _, rev = self.edge(state, action)
            versions.append(rev)
            if after is not None:
                after(i)
        distinct = set(versions)
        if len(distinct) > 1:
            return Scan('MIXED_REVISIONS', tuple(versions), 54,
                        'observations explicitly span different reported owner revisions')
        return Scan('OBSERVED_SINGLE_REVISION', tuple(versions), 54,
                    'consistent reported revision; continuity and origin not proved by response labels')


def main():
    from ab_chatbot_discovered_correspondence import DOMAIN, discover
    src = FiniteSystem((0, 0, 0))
    h = tuple((i, j, (k + i*j) % 3) for i,j,k in DOMAIN)
    owner = SourceOwnedHTTP(TransportedLaw(src.phi, h))
    with LoopbackHTTP(owner) as server:
        observer = RemoteObserver(server.url)
        old = observer.snapshot()
        prior = discover(src, lambda s,a: observer.edge(s,a,old.revision)[0], full=True)
        assert prior.status == 'FULL_CONJUGACY'
        bound = owner.bind(src, prior, old)
        first = owner.reenter(src, prior, bound, observer.snapshot(old.revision))
        assert first.status == 'SAME_PINNED_VERSION'
        owner.replace(TransportedLaw((0,1,0),h))
        old_again = observer.snapshot(old.revision)
        assert owner.reenter(src,prior,bound,old_again).status == 'SAME_PINNED_VERSION'
        now = observer.snapshot()
        moved = owner.reenter(src,prior,bound,now)
        assert moved.status == 'CHANGED'
        print('Real loopback HTTP server; source-owned immutable version; complete discovered H')
        print('Old revision:',old.revision,'historical reentry:', first.status)
        print('After mutation: historical:', old_again.revision, 'current:', now.revision, 'comparison:', moved.status)
        print('Total actual HTTP requests:',observer.calls)
        print('Scope: trusted local owner model, NOT authenticated external source or general A/B theory')


if __name__ == '__main__':
    main()
