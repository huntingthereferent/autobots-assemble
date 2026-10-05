from __future__ import annotations

import copy
from pathlib import Path

import pytest

from foundation.program_kernel.contracts import ContractError
from foundation.program_kernel.manifest import ManifestError, load_manifest
from foundation.program_kernel.runtime import execute


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "foundation" / "program_examples"


def test_stateless_shape_reuses_produced_value_as_next_input():
    manifest = load_manifest(EXAMPLES / "stateless.json")

    record = execute(manifest, {"text": "  ONE   two THREE "})

    assert record.values["normalized"] == "one two three"
    assert record.values["count"] == 3
    assert [step.operation for step in record.steps] == ["normalize", "count"]
    assert record.steps[0].produced == ["normalized"]
    assert record.steps[1].consumed == ["normalized"]
    assert all(witness["passed"] for witness in record.witnesses)


def test_stateful_shape_uses_same_kernel():
    manifest = load_manifest(EXAMPLES / "stateful.json")

    record = execute(manifest, {"delta": 2}, initial_state={"count": 5})

    assert record.values["count"] == 7
    assert len(record.steps) == 1
    assert all(witness["passed"] for witness in record.witnesses)


def test_event_device_shape_uses_same_kernel():
    manifest = load_manifest(EXAMPLES / "event_device.json")
    samples = [
        False, False,
        True, False, True, False,
        True, True, True, True,
    ]

    record = execute(manifest, {"samples": samples})

    assert record.values["toggle_count"] == 1
    assert record.values["led_on"] is True
    assert all(witness["passed"] for witness in record.witnesses)


def test_invalid_manifest_fails_before_execution(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"id": "broken"}', encoding="utf-8")

    with pytest.raises(ManifestError):
        load_manifest(bad)


def test_input_contract_mismatch_is_rejected():
    manifest = load_manifest(EXAMPLES / "stateless.json")

    with pytest.raises(ContractError):
        execute(manifest, {"text": 123})


def test_operation_output_contract_is_rejected():
    manifest = load_manifest(EXAMPLES / "stateless.json")
    changed = copy.deepcopy(manifest)
    changed["outputs"]["count"]["type"] = "string"

    with pytest.raises(ContractError):
        execute(changed, {"text": "one two three"})


def test_all_shapes_emit_same_execution_record_structure():
    cases = [
        (load_manifest(EXAMPLES / "stateless.json"), {"text": "one two three"}, None),
        (load_manifest(EXAMPLES / "stateful.json"), {"delta": 2}, {"count": 5}),
        (
            load_manifest(EXAMPLES / "event_device.json"),
            {"samples": [False, True, True, True]},
            None,
        ),
    ]

    for manifest, inputs, state in cases:
        record = execute(manifest, inputs, initial_state=state)
        assert record.manifest_id == manifest["id"]
        assert record.referent == manifest["referent"]
        assert record.steps
        assert record.witnesses
        assert isinstance(record.values, dict)
