from network import EvidenceRef, Protocol, Relation, RelationLedger, Witness, apply_protocol


def test_supported_movement_reenters_same_relation_network():
    protocol = Protocol("test.move", "closure test", ("spec", "acceptance"))
    source = EvidenceRef("spec:1", "fixture")
    result = apply_protocol(
        protocol,
        referent="problem:1",
        witnesses=(
            Witness("spec", "SUPPORTED", (source,)),
            Witness("acceptance", "SUPPORTED", (source,)),
        ),
        outputs=(Relation("problem:1", "status", "tested", "test", evidence=(source,)),),
        next_referent="problem:1:submission",
    )
    assert result.state == "MOVE"
    ledger = RelationLedger()
    snap = ledger.append(*result.as_relations())
    assert snap.latest("problem:1", "protocol_result").object == "MOVE"
    assert snap.latest("problem:1", "next_referent").object == "problem:1:submission"


def test_missing_required_witness_creates_wall_not_claimed_output():
    protocol = Protocol("test.wall", "wall test", ("client_file",))
    result = apply_protocol(
        protocol,
        referent="job:1",
        witnesses=(Witness("client_file", "MISSING", note="not supplied"),),
        outputs=(Relation("job:1", "status", "complete", "test"),),
    )
    assert result.state == "WALL"
    assert result.outputs == ()


def test_unknown_is_preserved():
    protocol = Protocol("test.unknown", "unknown test", ("correspondence",))
    result = apply_protocol(
        protocol,
        referent="relation:x",
        witnesses=(Witness("correspondence", "UNKNOWN"),),
    )
    assert result.state == "UNKNOWN"
