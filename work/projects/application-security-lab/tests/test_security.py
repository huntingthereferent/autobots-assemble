from pathlib import Path

from appsec_lab.audit import CONTROLLED_INPUT, build_report, write_report
from appsec_lab.db import build_fixture
from appsec_lab.secure import lookup_user
from appsec_lab.vulnerable import lookup_user_vulnerable


def test_normal_lookup_works_in_both_states():
    vulnerable_db = build_fixture()
    secure_db = build_fixture()

    assert lookup_user_vulnerable(vulnerable_db, "alice") == [
        {"id": 1, "username": "alice", "role": "user"}
    ]
    assert lookup_user(secure_db, "alice") == [
        {"id": 1, "username": "alice", "role": "user"}
    ]


def test_controlled_fixture_demonstrates_before_state():
    connection = build_fixture()

    rows = lookup_user_vulnerable(connection, CONTROLLED_INPUT)

    assert len(rows) == 3
    assert {row["username"] for row in rows} == {"alice", "bob", "admin"}


def test_parameterized_remediation_blocks_query_structure_change():
    connection = build_fixture()

    rows = lookup_user(connection, CONTROLLED_INPUT)

    assert rows == []


def test_security_report_records_before_after_and_control(tmp_path: Path):
    report = write_report(tmp_path / "security_report.json")

    assert report["before"]["vulnerable"] is True
    assert report["before"]["rows_returned"] == 3
    assert report["remediation"]["control"] == "parameterized SQL"
    assert report["after"]["controlled_input_rows_returned"] == 0
    assert report["after"]["normal_lookup_rows_returned"] == 1
    assert report["after"]["regression_blocked"] is True
    assert (tmp_path / "security_report.json").is_file()


def test_in_memory_report_is_deterministic():
    first = build_report()
    second = build_report()

    assert first == second
