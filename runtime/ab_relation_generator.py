"""Evidence-derived, domain-neutral inverse A/B construction proposals.

This is the missing default generator: no game, website, school, or factory
templates. It only recombines RELATION VALUES that were actually witnessed
within the same sufficient A/B proof block. Such combinations are hypothetical;
the witness contract NEVER guarantees that the resulting structure is valid.

Missing connections/relations are walls to investigate, not permission to
invent mechanisms. Follow-up execution always uses an independent evaluator.
"""
from __future__ import annotations

from itertools import product
from hashlib import sha256
import json
from typing import Any, Iterable

from .ab_construction import ConstructionProposal, inverse_fibers, project_candidates
from .ab_information import ABOccurrence, ABInformationState


def _key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def derive_relation_constructions(
    occurrences: Iterable[ABOccurrence],
    state: ABInformationState,
    *,
    source_locators: Iterable[str],
    witness_contract: str,
    horizon: int,
    intent: str,
    max_candidates: int = 32,
    max_scan_per_block: int = 4096,
) -> tuple[ConstructionProposal, ...]:
    """Generate novel, source-addressed relation tuples without a domain generator.

    Given a sufficient proof partition P from forward A/B, fix one minimal
    proving relation subset and recombine non-proving relation dimensions
    using values *witnessed inside the same proof block*. The quotient itself
    gives the preservation hypothesis; it does NOT warrant that an unobserved
    tuple will preserve the predicted continuation.

    Returns no proposals if there is no tested recombination to make.
    Every value carries a concrete source locator. Caller must use existing
    A/B observations to test the proposed tuple in its native referent.
    """
    group = tuple(occurrences)
    locators = tuple(source_locators)
    fibers = inverse_fibers(
        group, state, source_locators=locators,
        witness_contract=witness_contract, horizon=horizon,
    )
    if not 1 <= max_scan_per_block <= 100000:
        raise ValueError("max_scan_per_block must be bounded and positive")
    if not group:
        return ()
    keys = set(dict(group[0].relations))
    if any(set(dict(occurrence.relations)) != keys for occurrence in group):
        raise ValueError("missing relation fields: cannot assume absent values")
    if len(keys) > 16:
        raise ValueError("relation construction exceeds bounded dimension count")
    # Non-JSON values are not silently stringified into speculative facts.
    for occurrence in group:
        _key(dict(occurrence.relations))
    original_relations = {
        _key(dict(occurrence.relations)) for occurrence in group
    }
    # A/B's existing coarsest sufficient partition; no extra category math.
    proof = state.proofs[0]
    protected = tuple(proof.sources[0])
    if any(name not in keys for name in protected):
        raise ValueError("proof refers to an unobserved relation")
    class_by_index = {
        index: category
        for category, block in enumerate(state.continuation_partition)
        for index in block
    }

    def construct(fiber):
        for block in proof.partition:
            members = tuple(index for index in block
                            if class_by_index[index] == fiber.category)
            # Crossing a proof block would discard tested distinctions.
            if len(members) < 2 or len(members) != len(block):
                continue
            observations = {index: dict(group[index].relations) for index in members}
            varying = []
            domains = []
            for name in sorted(keys):
                if name in protected:
                    continue
                values_by_key = {}
                for index in members:
                    value = observations[index][name]
                    values_by_key.setdefault(_key(value), (value, index))
                if len(values_by_key) > 1:
                    varying.append(name)
                    domains.append(tuple(values_by_key[k] for k in sorted(values_by_key)))
            if len(varying) < 2:
                # No new mixed relation tuple is possible from only one axis.
                continue
            baseline = dict(observations[members[0]])
            protected_witness = members[0]
            scanned = 0
            for combination in product(*domains):
                scanned += 1
                if scanned > max_scan_per_block:
                    break
                relation_values = dict(baseline)
                by_field = {
                    name: locators[protected_witness] for name in sorted(keys)
                }
                for name, (value, index) in zip(varying, combination):
                    relation_values[name] = value
                    by_field[name] = locators[index]
                if _key(relation_values) in original_relations:
                    continue
                yield {
                    "kind": "relation-recombination",
                    "relation_values": relation_values,
                    "construction_contract": "UNVERIFIED candidate; no native observation",
                    "proof_source_names": list(protected),
                    "proof_block_source_indices": list(members),
                    "component_source_locators": by_field,
                }

    return project_candidates(
        fibers, construct, intent=intent, max_candidates=max_candidates,
    )


def derive_exploratory_constructions(
    occurrences: Iterable[ABOccurrence],
    state: ABInformationState,
    *,
    source_locators: Iterable[str],
    witness_contract: str,
    horizon: int,
    intent: str,
    max_candidates: int = 32,
    max_scan: int = 4096,
) -> tuple[ConstructionProposal, ...]:
    """Cross witnessed A/B continuation classes, with NO category inheritance.

    This is a *hypothesis generator*, not an inverse that preserves known
    continuation equivalence. The same source relation vocabulary and values
    are used, but a proposed combination must NOT be realizable entirely
    inside any one existing continuation fiber. If the old evidence has
    only one class, there is no witnessed boundary to cross.

    There is deliberately no predicted continuation; all candidates have
    category=None, are PROPOSED, and require a new independent witness.
    """
    if intent not in {"construct", "synthesize", "simulate", "alternatives"}:
        raise ValueError("exploratory construction needs explicit construction intent")
    if not 1 <= max_candidates <= 1000 or not 1 <= max_scan <= 100000:
        raise ValueError("exploratory generation limits must be positive and bounded")
    group = tuple(occurrences)
    locators = tuple(source_locators)
    fibers = inverse_fibers(
        group, state, source_locators=locators,
        witness_contract=witness_contract, horizon=horizon,
    )
    if len(fibers) < 2:
        return ()
    keys = set(dict(group[0].relations))
    if not keys or len(keys) > 16:
        raise ValueError("relation dimensions are missing or exceed the safety limit")
    if any(set(dict(item.relations)) != keys for item in group):
        raise ValueError("missing relation fields: cannot infer absent values")
    canonical = tuple(sorted(keys))
    observed = tuple(dict(item.relations) for item in group)
    domains = []
    for name in canonical:
        values_by_key: dict[str, tuple[Any, int]] = {}
        for index, row in enumerate(observed):
            value = row[name]
            values_by_key.setdefault(_key(value), (value, index))
        domains.append(tuple(values_by_key[value] for value in sorted(values_by_key)))
    originals = {_key(row) for row in observed}
    class_by_source = {
        index: fiber.category
        for fiber in fibers for index in fiber.source_indices
    }
    in_fiber_values = tuple({
        name: {_key(observed[index][name]) for index in fiber.source_indices}
        for name in canonical
    } for fiber in fibers)

    out: list[ConstructionProposal] = []
    for scan, components in enumerate(product(*domains), start=1):
        if scan > max_scan or len(out) >= max_candidates:
            break
        relation_values = {
            name: value for name, (value, _) in zip(canonical, components)
        }
        if _key(relation_values) in originals:
            continue
        # Only genuine boundary-crossing combinations belong to explore.
        if any(
            all(_key(relation_values[name]) in within[name] for name in canonical)
            for within in in_fiber_values
        ):
            continue
        component_indices = tuple(sorted({
            index for _value, index in components
        }))
        component_sources = {
            name: locators[index]
            for name, (_value, index) in zip(canonical, components)
        }
        touched_categories = sorted({
            class_by_source[index] for index in component_indices
        })
        if len(touched_categories) < 2:
            # Source selection did not actually span different categories.
            continue
        structure = {
            "kind": "cross-category-recombination",
            "relation_values": relation_values,
            "construction_contract": "UNVERIFIED cross-category hypothesis",
            "prior_continuation_category": "UNASSIGNED",
            "requires_independent_observation": True,
            "source_categories_touched": touched_categories,
            "component_source_locators": component_sources,
        }
        proposal_payload = {
            "referent": state.referent,
            "category": None,
            "source_indices": component_indices,
            "source_locators": tuple(locators[i] for i in component_indices),
            "witness_contract": witness_contract,
            "horizon": horizon,
            "structure": structure,
        }
        identity = sha256(
            json.dumps(
                proposal_payload, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        out.append(ConstructionProposal(
            proposal_id=identity,
            referent=state.referent,
            category=None,
            structure=structure,
            source_indices=component_indices,
            source_locators=tuple(locators[i] for i in component_indices),
            witness_contract=witness_contract,
            horizon=horizon,
        ))
    return tuple(out)
