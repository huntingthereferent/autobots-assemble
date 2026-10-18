"""B7: an invoked, source-scoped continuation cycle over the EXISTING runtime journal.

Never runs workers, manufactures native proof, authenticates owners, or creates
an always-on scheduler. Each write is delegated to existing B2/B4 gates.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
import json
from typing import Any

NATIVE_RETURN = 'WORKSTATION_NATIVE_RESULT_VERIFIED'
DERIVED_RELATION = 'WORKSTATION_RETURN_RELATION_ADMITTED'
NATIVE_ASSIGNMENT = 'WORKSTATION_NATIVE_HELP_ASSIGNED'
OPEN_HELP = 'WORKSTATION_HELP_OPEN'
OWNER_WALL = 'WORKSTATION_OWNER_CANDIDATE_BINDING_WALL'
CONTINUATION_LANE = 'workstation-continuation-lane/v1'
OWNER_CAPABILITY = 'owner-native-correspondence-witness'


@dataclass(frozen=True)
class CycleReport:
    status: str
    passes: int
    journal_events_added: int
    derived_return_lanes: tuple[str, ...]
    unresolved_return_lanes: tuple[str, ...]
    awaiting_native_execution: tuple[str, ...]
    awaiting_source_owner: tuple[str, ...]
    preserved_wall_lanes: tuple[str, ...]
    native_worker_executed: bool = False
    native_checkpoint_pass: bool = False


class WorkstationCycle:
    """Repeat already-authorized B2/B4 passes until no new journal entries arise.

    This controller is intentionally sequential and *invoked*. The caller must
    bind the real native verifier callbacks into B2/B4. This controller does
    not itself have an execution authorization surface.
    """

    def __init__(self, harness: Any, *, return_continuation: Any = None,
                 verify_wall_resolution: Any = None):
        if not callable(getattr(harness, '_runtime', None)) or not callable(getattr(harness, 'tick', None)):
            raise TypeError('existing workstation harness and native B2 movement required')
        if return_continuation is not None and (
            getattr(return_continuation, 'harness', None) is not harness
            or not callable(getattr(return_continuation, 'derive_next', None))
            or not callable(getattr(return_continuation, 'next_pass', None))
        ):
            raise ValueError('B4 must be bound to this exact workstation harness')
        if verify_wall_resolution is not None and not callable(verify_wall_resolution):
            raise TypeError("independent wall-resolution verifier required")
        self.verify_wall_resolution = verify_wall_resolution
        self.harness = harness
        self.b4 = return_continuation

    def _snapshot(self) -> tuple[Any, tuple[Any, ...], tuple[tuple[str, str], ...], dict[str, str]]:
        runtime = self.harness._runtime()
        if not callable(getattr(runtime, 'get', None)):
            raise TypeError('real-runtime-compatible handoff lookup required')
        events = tuple(runtime.event_store.all())
        tokens: list[tuple[str, str]] = []
        seen: set[str] = set()
        for e in events:
            if not is_dataclass(e):
                raise ValueError('native journal must expose HandoffEvent dataclasses')
            event_id = getattr(e, 'event_id', None)
            lane_id = getattr(e, 'handoff_id', None)
            if not isinstance(event_id, str) or not event_id or event_id in seen:
                raise ValueError('journal has missing or duplicate native event identities')
            if not isinstance(lane_id, str) or not lane_id:
                raise ValueError('journal event has no handoff identity')
            seen.add(event_id)
            payload = json.dumps(asdict(e), sort_keys=True, separators=(',', ':'),
                                 ensure_ascii=False, allow_nan=False)
            tokens.append((event_id, sha256(payload.encode('utf-8')).hexdigest()))
        specs: dict[str, str] = {}
        for hid, handoff in runtime._handoffs.items():
            if not is_dataclass(handoff) or hid != getattr(handoff, 'handoff_id', None):
                raise ValueError('invalid native handoff specification')
            raw = json.dumps(asdict(handoff), sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False, allow_nan=False)
            specs[hid] = sha256(raw.encode('utf-8')).hexdigest()
        return runtime, events, tuple(tokens), specs

    @staticmethod
    def _workstation_events(runtime: Any, events: tuple[Any, ...]) -> dict[str, list[Any]]:
        groups: dict[str, list[Any]] = {}
        for e in events:
            h = runtime.get(e.handoff_id)
            if getattr(h, 'metadata', {}).get('source_system') == CONTINUATION_LANE:
                groups.setdefault(e.handoff_id, []).append(e)
        return groups

    def _blocked(self, runtime: Any, events: tuple[Any, ...]):
        groups = self._workstation_events(runtime, events)
        pending, jobs, owner, walls = [], set(), [], []
        for lane_id, history in sorted(groups.items()):
            types = {e.event_type for e in history}
            # History is retained; only a fresh, exact-wall native check can
            # release a wall. Labels or later unrelated success cannot do so.
            active_walls = [e for e in history if e.event_type == OWNER_WALL
                            and not (self.verify_wall_resolution is not None
                                     and self.verify_wall_resolution(runtime, e) is True)]
            if NATIVE_RETURN in types and DERIVED_RELATION not in types and not active_walls:
                pending.append(lane_id)
            if active_walls:
                walls.append(lane_id)
            if not active_walls and any(
                e.event_type == OPEN_HELP
                and e.data.get('capability') == OWNER_CAPABILITY
                for e in history
            ):
                owner.append(lane_id)
            if NATIVE_RETURN not in types:
                for e in history:
                    if e.event_type == NATIVE_ASSIGNMENT:
                        job_id = e.data.get('job_id')
                        if not isinstance(job_id, str) or not job_id:
                            raise ValueError('source-owned native assignment has no exact job id')
                        jobs.add(job_id)
        return pending, sorted(jobs), owner, walls

    def run(self, *, max_passes: int = 8, max_new_events: int = 64) -> CycleReport:
        if type(max_passes) is not int or not 1 <= max_passes <= 64:
            raise ValueError('max_passes must be an integer in [1,64]')
        if type(max_new_events) is not int or not 1 <= max_new_events <= 1000:
            raise ValueError('max_new_events must be an integer in [1,1000]')
        _, first, initial, initial_specs = self._snapshot()
        derived: set[str] = set()
        unresolved: set[str] = set()
        passes = 0
        stop = 'QUIESCENT'
        for iteration in range(max_passes):
            passes = iteration + 1
            current_runtime, before, before_tokens, before_specs = self._snapshot()
            if any(before_specs.get(k) != v for k, v in initial_specs.items()):
                raise ValueError('journal handoff specification rewritten or removed')
            if before_tokens[:len(initial)] != initial:
                raise ValueError('journal prefix rewound, reordered or rewritten')
            if self.b4 is None:
                self.harness.tick()
            else:
                pending, _, _, _ = self._blocked(current_runtime, before)
                for lane in pending:
                    result = self.b4.derive_next(lane)
                    if result['state'] in ('NEXT_RELATION_RECORDED', 'ALREADY_RECORDED'):
                        derived.add(lane)
                    elif result['state'] == 'NO_ADMITTED_NEXT_RELATION':
                        unresolved.add(lane)
                    else:
                        raise ValueError('unrecognized B4 derivation state')
                self.b4.next_pass()
            _, after, after_tokens, after_specs = self._snapshot()
            if any(after_specs.get(k) != v for k, v in before_specs.items()):
                raise ValueError('journal handoff specification rewritten or removed during pass')
            if after_tokens[:len(before_tokens)] != before_tokens:
                raise ValueError('journal was rewritten, reordered, or truncated during a pass')
            if len(after_tokens) - len(initial) >= max_new_events:
                stop = 'BOUND_REACHED'
                break
            if after_tokens == before_tokens:
                break
        else:
            stop = 'BOUND_REACHED'
        final_runtime, final_events, final_tokens, final_specs = self._snapshot()
        if any(final_specs.get(k) != v for k, v in initial_specs.items()):
            raise ValueError('journal handoff specification rewritten or removed since controller began')
        if final_tokens[:len(initial)] != initial:
            raise ValueError('journal changed since controller began')
        pending, jobs, owners, walls = self._blocked(final_runtime, final_events)
        if stop == 'QUIESCENT' and (pending or unresolved or jobs or owners or walls):
            stop = 'WAITING_FOR_EVIDENCE_OR_AUTHORIZATION'
        return CycleReport(
            status=stop, passes=passes,
            journal_events_added=len(final_tokens) - len(initial),
            derived_return_lanes=tuple(sorted(derived)),
            unresolved_return_lanes=tuple(sorted(set(pending) | unresolved)),
            awaiting_native_execution=tuple(jobs),
            awaiting_source_owner=tuple(owners),
            preserved_wall_lanes=tuple(walls),
        )
