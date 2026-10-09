"""Cyclic Action Engine: witnessed native B-continuation over declared bounded window spaces.

The entry points start() and resume() own the same mathematical operation.
A serialized result is evidence, not permission to invent equivalence: resume
replays it against the original window laws and B-invariant carrier before
advancing. This is a B-only research kernel, not full simultaneous A/B
conjugacy, a universal engine, an agent, or native ARC gameplay.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json

from .window_two import WindowProcess

State = tuple[int, ...]


def _wire(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _law_wire(law: WindowProcess) -> dict:
    return {"gain": law.gain, "stem": [list(q) for q in law.stem],
            "period": [list(q) for q in law.period]}


def _law_read(raw: dict) -> WindowProcess:
    if not isinstance(raw, dict) or set(raw) != {"gain", "stem", "period"}:
        raise ValueError("invalid frozen mathematical law")
    law = WindowProcess(raw["gain"], tuple(tuple(q) for q in raw["stem"]),
                        tuple(tuple(q) for q in raw["period"]))
    if _law_wire(law) != raw:
        raise ValueError("noncanonical mathematical law")
    return law


def _state_read(raw: object, dimension: int) -> State:
    if not isinstance(raw, list) or len(raw) != dimension or any(
            type(x) is not int or x not in (0, 1, 2) for x in raw):
        raise ValueError("invalid finite-field state")
    return tuple(raw)


def _carrier_read(raw: object) -> tuple[State, ...]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("WATCH requires a nonempty carrier")
    if not isinstance(raw[0], list):
        raise ValueError("WATCH carrier must contain states")
    dimension = len(raw[0])
    if dimension < 3:
        raise ValueError("two-input window requires at least three coordinates")
    states = tuple(_state_read(s, dimension) for s in raw)
    if len(states) != len(set(states)) or states != tuple(sorted(states)):
        raise ValueError("WATCH carrier must be distinct and canonical")
    return states


def _question(left: WindowProcess, right: WindowProcess,
              carrier: tuple[State, ...]) -> dict:
    return {"operation": "B_SUCCESSIVE_COMPOSITION", "source": _law_wire(left),
            "target": _law_wire(right), "carrier": [list(s) for s in carrier],
            "relation": "B_ONLY_ON_DECLARED_INVARIANT_CARRIER"}


def _question_id(question: dict) -> str:
    return sha256(_wire(question).encode("utf-8")).hexdigest()


def _validate_carrier(left: WindowProcess, right: WindowProcess,
                      carrier: tuple[State, ...]) -> None:
    size = len(carrier[0])
    if any(len(s) != size for s in carrier):
        raise ValueError("mixed carrier dimensions")
    members = set(carrier)
    for law in (left, right):
        if any(law.step(s, "B") not in members for s in carrier):
            raise ValueError("WATCH is not B-invariant for both laws")


def _cycles(law: WindowProcess, carrier: tuple[State, ...]
           ) -> tuple[tuple[State, ...], ...]:
    remaining = set(carrier)
    result = []
    while remaining:
        first = min(remaining)
        cycle = []
        current = first
        while current not in cycle:
            if current not in remaining:
                raise AssertionError("B failed to act as a permutation on carrier")
            cycle.append(current)
            current = law.step(current, "B")
        if current != first:
            raise AssertionError("B orbit did not close at its first state")
        remaining.difference_update(cycle)
        result.append(tuple(cycle))
    return tuple(sorted(result, key=lambda c: (len(c), c[0])))


def _conjugacy(left: WindowProcess, right: WindowProcess,
               carrier: tuple[State, ...]) -> list:
    lc, rc = _cycles(left, carrier), _cycles(right, carrier)
    if [len(c) for c in lc] != [len(c) for c in rc]:
        raise AssertionError("equal periodic observations reached cycle closure with unequal cycles")
    mapping = {a: b for x, y in zip(lc, rc) for a, b in zip(x, y)}
    if len(mapping) != len(carrier) or set(mapping.values()) != set(carrier):
        raise AssertionError("candidate B conjugacy does not give a bijection")
    if any(mapping[left.step(x, "B")] != right.step(mapping[x], "B") for x in carrier):
        raise AssertionError("constructed B conjugacy does not intertwine B")
    return [[list(x), list(mapping[x])] for x in carrier]


def _observation(left: WindowProcess, right: WindowProcess,
                 carrier: tuple[State, ...], left_images: list[State],
                 right_images: list[State], n: int) -> dict:
    lf = [list(state) for state, image in zip(carrier, left_images) if state == image]
    rf = [list(state) for state, image in zip(carrier, right_images) if state == image]
    return {"power": n, "source_fixed": lf, "target_fixed": rf,
            "source_anchor_image": list(left_images[0]),
            "target_anchor_image": list(right_images[0])}


def _advance(left: WindowProcess, right: WindowProcess,
             carrier: tuple[State, ...], records: list[dict],
             max_power: int) -> tuple[list[dict], str, list]:
    left_images, right_images = list(carrier), list(carrier)
    for n, stored in enumerate(records, 1):
        left_images = [left.step(x, "B") for x in left_images]
        right_images = [right.step(x, "B") for x in right_images]
        real = _observation(left, right, carrier, left_images, right_images, n)
        if real != stored:
            raise ValueError(f"saved witness B^{n} failed mathematical replay")
        lf, rf = len(real["source_fixed"]), len(real["target_fixed"])
        if lf != rf and n != len(records):
            raise ValueError("record illegally continued past a decisive obstruction")
        if lf == rf == len(carrier) and n != len(records):
            raise ValueError("record illegally continued past verified cycle closure")
    if records:
        last = records[-1]
        if len(last["source_fixed"]) != len(last["target_fixed"]):
            return records, "DISTINGUISHED_B_ACTIONS", []
        if len(last["source_fixed"]) == len(carrier):
            return records, "B_ONLY_CONJUGACY_WITNESSED", _conjugacy(left, right, carrier)
    for n in range(len(records) + 1, max_power + 1):
        left_images = [left.step(x, "B") for x in left_images]
        right_images = [right.step(x, "B") for x in right_images]
        reading = _observation(left, right, carrier, left_images, right_images, n)
        records.append(reading)
        if len(reading["source_fixed"]) != len(reading["target_fixed"]):
            return records, "DISTINGUISHED_B_ACTIONS", []
        if len(reading["source_fixed"]) == len(carrier):
            return records, "B_ONLY_CONJUGACY_WITNESSED", _conjugacy(left, right, carrier)
    return records, "UNKNOWN_BUDGET", []


@dataclass(frozen=True)
class ResearchResult:
    """Witness-bearing serialized research record; no Engine 1 dependency."""
    record: dict

    @property
    def status(self) -> str:
        return self.record["status"]

    @property
    def powers_examined(self) -> int:
        return len(self.record["observations"])

    def serialize(self) -> str:
        return _wire(self.record)


class CyclicActionEngine:
    """Native research execution: continue the SAME admitted B relation."""

    @staticmethod
    def fiber(depth: int, *, first: int = 0) -> tuple[State, ...]:
        if type(depth) is not int or not 3 <= depth <= 8:
            raise ValueError("bounded fiber dimension must be 3..8")
        if type(first) is not int or first not in (0, 1, 2):
            raise ValueError("fiber coordinate must lie in F3")
        return tuple((first, *r) for r in product(range(3), repeat=depth - 1))

    def start(self, left: WindowProcess, right: WindowProcess,
              carrier: tuple[State, ...], max_power: int) -> ResearchResult:
        if type(max_power) is not int or max_power < 1:
            raise ValueError("a positive integer continuation budget is required")
        # Build the same normalized question as re-entry will validate.
        question = _question(left, right, _carrier_read([list(s) for s in carrier]))
        canonical_carrier = _carrier_read(question["carrier"])
        _validate_carrier(left, right, canonical_carrier)
        observations, status, bijection = _advance(
            left, right, canonical_carrier, [], max_power)
        return ResearchResult({"schema": 1, "question": question,
                               "question_id": _question_id(question),
                               "status": status, "max_power": max_power,
                               "observations": observations,
                               "B_bijection": bijection,
                               "simultaneous_A_B": "UNKNOWN_NOT_WATCHED"})

    def resume(self, serialized: str, max_power: int,
               *, expected_question_id: str | None = None) -> ResearchResult:
        if type(max_power) is not int or max_power < 1:
            raise ValueError("a positive integer continuation budget is required")
        try:
            record = json.loads(serialized)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid saved research record") from exc
        if not isinstance(record, dict) or set(record) != {
                "schema", "question", "question_id", "status", "max_power",
                "observations", "B_bijection", "simultaneous_A_B"}:
            raise ValueError("missing/unknown fields in research record")
        if type(record["schema"]) is not int or record["schema"] != 1:
            raise ValueError("unknown research record schema")
        question = record["question"]
        if not isinstance(question, dict) or set(question) != {
                "operation", "source", "target", "carrier", "relation"}:
            raise ValueError("invalid saved research question")
        if question["operation"] != "B_SUCCESSIVE_COMPOSITION" or question["relation"] != "B_ONLY_ON_DECLARED_INVARIANT_CARRIER":
            raise ValueError("cannot silently change the watched mathematical relation")
        identifier = _question_id(question)
        if identifier != record["question_id"] or (
                expected_question_id is not None and identifier != expected_question_id):
            raise ValueError("saved question differs from anchored original")
        left, right = _law_read(question["source"]), _law_read(question["target"])
        carrier = _carrier_read(question["carrier"])
        _validate_carrier(left, right, carrier)
        observations = record["observations"]
        if (type(record["max_power"]) is not int or record["max_power"] < 1 or
                not isinstance(observations, list) or not observations or
                len(observations) > record["max_power"] or max_power < len(observations)):
            raise ValueError("bad saved observation history/budget")
        if record["simultaneous_A_B"] != "UNKNOWN_NOT_WATCHED":
            raise ValueError("B-only research cannot certify simultaneous A/B")
        replay, status, bijection = _advance(left, right, carrier,
                                             list(observations), len(observations))
        if (record["status"] != status or record["B_bijection"] != bijection or
                (status == "UNKNOWN_BUDGET" and len(observations) != record["max_power"])):
            raise ValueError("record status or positive witness failed verification")
        full, status, bijection = _advance(left, right, carrier, replay, max_power)
        return ResearchResult({"schema": 1, "question": question,
                               "question_id": identifier, "status": status,
                               "max_power": max_power, "observations": full,
                               "B_bijection": bijection,
                               "simultaneous_A_B": "UNKNOWN_NOT_WATCHED"})
