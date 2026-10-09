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
