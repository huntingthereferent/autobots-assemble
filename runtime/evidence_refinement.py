"""Evidence-refinement implementation. The old `runtime.ab_information` path is a compatibility alias."""

from __future__ import annotations


"""Generic information-minimal witnessed evidence refinement.

Promoted from the ARC cross-game evidence into Continuity without game
semantics.  The operation works on witnessed occurrences:

    current referent
    + available relations
    + witnessed continuation

It keeps the coarsest sufficient evidence partition that makes continuation
deterministic, preserves every minimal source-set realizing that partition, and
can synthesize the continuation quotient when old relation vocabulary is too
fine.

This module is evidence/refinement logic. It is not an agent scheduler.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable


@dataclass(frozen=True)
class EvidenceOccurrence:
    referent: Any
    relations: tuple[tuple[str, Any], ...]
    continuation: Any

    @classmethod
    def create(
        cls,
        *,
        referent: Any,
        relations: dict[str, Any],
        continuation: Any,
    ) -> "EvidenceOccurrence":
        return cls(
            referent=referent,
            relations=tuple(sorted(relations.items())),
            continuation=continuation,
        )


@dataclass(frozen=True)
class EvidenceProof:
    partition: tuple[tuple[int, ...], ...]
    sources: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class EvidenceRefinementState:
    referent: Any
    continuation_partition: tuple[tuple[int, ...], ...]
    proofs: tuple[EvidenceProof, ...]
    synthesized: bool = False


@dataclass(frozen=True)
class SynthesizedRelation:
    referent: Any
    proof_partition: tuple[tuple[int, ...], ...]
    continuation_partition: tuple[tuple[int, ...], ...]
    proof_to_class: tuple[tuple[int, int], ...]


def _freeze(value: Any) -> str:
    """Stable comparison key for arbitrary witnessed values."""

    return repr(value)


def _partition_for(
    group: tuple[EvidenceOccurrence, ...],
    subset: tuple[str, ...],
) -> tuple[tuple[int, ...], ...]:
    buckets: dict[Any, list[int]] = defaultdict(list)
    for index, occurrence in enumerate(group):
        relations = dict(occurrence.relations)
        key = tuple((name, _freeze(relations[name])) for name in subset)
        buckets[key].append(index)
    return tuple(sorted(tuple(block) for block in buckets.values()))


def continuation_partition(
    group: Iterable[EvidenceOccurrence],
) -> tuple[tuple[int, ...], ...]:
    occurrences = tuple(group)
    buckets: dict[str, list[int]] = defaultdict(list)
    for index, occurrence in enumerate(occurrences):
        buckets[_freeze(occurrence.continuation)].append(index)
    return tuple(sorted(tuple(block) for block in buckets.values()))


def partition_is_sufficient(
    group: tuple[EvidenceOccurrence, ...],
    partition: tuple[tuple[int, ...], ...],
) -> bool:
    for block in partition:
        continuations = {
            _freeze(group[index].continuation)
            for index in block
        }
        if len(continuations) > 1:
            return False
    return True


def partition_refines(
    fine: tuple[tuple[int, ...], ...],
    coarse: tuple[tuple[int, ...], ...],
) -> bool:
    coarse_sets = [set(block) for block in coarse]
    return all(
        any(set(block).issubset(container) for container in coarse_sets)
        for block in fine
    )


def information_closure(
    group: Iterable[EvidenceOccurrence],
) -> EvidenceRefinementState:
    """Return the coarsest available evidence partition(s).

    Relation count is not the optimization target. A one-name proof may carry
    more unnecessary distinction than another one-name proof. We therefore
    compare the partitions induced by all witnessed relation subsets and retain
    only sufficient partitions that are not strict refinements of another
    sufficient partition.
    """

    occurrences = tuple(group)
    if not occurrences:
        raise ValueError("at least one witnessed occurrence is required")

    referent = occurrences[0].referent
    if any(item.referent != referent for item in occurrences):
        raise ValueError("information_closure requires one referent family")

    target = continuation_partition(occurrences)
    if len(target) <= 1:
        whole = (tuple(range(len(occurrences))),)
        return EvidenceRefinementState(
            referent=referent,
            continuation_partition=target,
            proofs=(EvidenceProof(whole, ((),)),),
        )

    common_names = set(dict(occurrences[0].relations))
    for occurrence in occurrences[1:]:
        common_names.intersection_update(dict(occurrence.relations))
    names = tuple(sorted(common_names))

    by_partition: dict[
        tuple[tuple[int, ...], ...],
        list[tuple[str, ...]],
    ] = defaultdict(list)

    for size in range(1, len(names) + 1):
        for subset in combinations(names, size):
            partition = _partition_for(occurrences, subset)
            if partition_is_sufficient(occurrences, partition):
                by_partition[partition].append(subset)

    if not by_partition:
        raise ValueError(("witness contract insufficient", referent))

    partitions = tuple(by_partition)
    survivors = tuple(
        partition
        for partition in partitions
        if not any(
            partition != other
            and partition_refines(partition, other)
            for other in partitions
        )
    )

    proofs: list[EvidenceProof] = []
    for partition in survivors:
        raw_sources = sorted(
            by_partition[partition],
            key=lambda source: (len(source), source),
        )
        minimal_sources: list[tuple[str, ...]] = []
        for source in raw_sources:
            source_set = set(source)
            if any(
                set(existing).issubset(source_set)
                for existing in minimal_sources
            ):
                continue
            minimal_sources.append(source)
        proofs.append(
            EvidenceProof(
                partition=partition,
                sources=tuple(minimal_sources),
            )
        )

    proofs.sort(
        key=lambda proof: (
            len(proof.partition),
            proof.partition,
            proof.sources,
        )
    )
    return EvidenceRefinementState(
        referent=referent,
        continuation_partition=target,
        proofs=tuple(proofs),
    )


def synthesize_continuation_relation(
    state: EvidenceRefinementState,
) -> SynthesizedRelation | None:
    """Merge a sufficient proof partition down to the continuation quotient.

    Returns None when an existing proof already realizes the continuation
    partition exactly.
    """

    exact = [
        proof
        for proof in state.proofs
        if proof.partition == state.continuation_partition
    ]
    if exact:
        return None

    proof = state.proofs[0]
    target_sets = [
        set(block)
        for block in state.continuation_partition
    ]
    mapping: list[tuple[int, int]] = []

    for proof_index, proof_block in enumerate(proof.partition):
        block_set = set(proof_block)
        hits = [
            target_index
            for target_index, target in enumerate(target_sets)
            if block_set.issubset(target)
        ]
        if len(hits) != 1:
            raise ValueError(
                (
                    "proof block is not continuation-pure",
                    proof_block,
                    hits,
                )
            )
        mapping.append((proof_index, hits[0]))

    return SynthesizedRelation(
        referent=state.referent,
        proof_partition=proof.partition,
        continuation_partition=state.continuation_partition,
        proof_to_class=tuple(mapping),
    )


def apply_synthesized(
    relation: SynthesizedRelation,
    occurrence_index: int,
) -> int:
    proof_index = next(
        index
        for index, block in enumerate(relation.proof_partition)
        if occurrence_index in block
    )
    return dict(relation.proof_to_class)[proof_index]
