"""B14 explicit local operator entrance: public-pin policy and B13 delivery.

Public keys must be checked out of band. This CLI neither creates a signing
key nor asserts the claimed operator reference is an authenticated identity.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from systems.workspace.b12_b3_native_delivery import SOURCE_NAME
from systems.workspace.b13_offline_owner_delivery import (
    load_operator_pin, load_signed_envelope,
)
from systems.workspace.b14_operator_pin_ledger import (
    B14OperatorTrustedDelivery, OperatorPinLedger,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B14 operator pin ledger and explicit native B13 delivery")
    ap.add_argument("--trust-ledger", required=True, type=Path)
    areas = ap.add_subparsers(dest="area", required=True)
    pin = areas.add_parser("pin", help="operator-confirmed PUBLIC pin lifecycle")
    pin.add_argument("--source-name", default=SOURCE_NAME)
    pin.add_argument("--source-edition", required=True)
    pin_modes = pin.add_subparsers(dest="pin_action", required=True)
    pin_modes.add_parser("status")
    for action in ("enroll", "rotate", "revoke"):
        sub = pin_modes.add_parser(action)
        sub.add_argument("--operator-ref", required=True)
        sub.add_argument("--verification-ref", required=True)
        if action != "revoke":
            sub.add_argument("--public-key", required=True, type=Path)
            sub.add_argument("--expected-public-key-sha256", required=True)
            sub.add_argument("--confirm-new-sha256", required=True)
        if action != "enroll":
            sub.add_argument("--confirm-prior-sha256", required=True)

    native = areas.add_parser("native", help="one previously executed B3 source result")
    native.add_argument("--construction-dir", required=True, type=Path)
    native.add_argument("--native-data-dir", required=True, type=Path)
    native.add_argument("--observed-journal", required=True, type=Path)
    native.add_argument("--lane-id", required=True)
    native.add_argument("--opening-id", required=True)
    native.add_argument("--job-id", required=True)
    native.add_argument("--confirm-source-job", required=True)
    native.add_argument("--pinned-public-key", required=True, type=Path)
    native.add_argument("--expected-public-key-sha256", required=True)
    actions = native.add_subparsers(dest="native_action", required=True)
    prep = actions.add_parser("prepare")
    prep.add_argument("--goal-id", required=True)
    prep.add_argument("--candidate-id", required=True)
    prep.add_argument("--route-node", required=True, action="append")
    sign = actions.add_parser("signing-request")
    sign.add_argument("--request-id", required=True)
    deliver = actions.add_parser("deliver")
    deliver.add_argument("--request-id", required=True)
    deliver.add_argument("--confirm-request", required=True)
    deliver.add_argument("--approve-native-delivery", action="store_true")
    deliver.add_argument("--signed-envelope", required=True, type=Path)

    args = ap.parse_args(argv)
    if args.area == "pin":
        ledger = OperatorPinLedger(args.trust_ledger)
        if args.pin_action == "status":
            result = {
                "source_name": args.source_name,
                "source_edition": args.source_edition,
                "current_public_key_sha256":
                    ledger.current(args.source_name, args.source_edition),
                "operator_source_identity_authenticated": False,
            }
        elif args.pin_action in ("enroll", "rotate"):
            public = load_operator_pin(
                args.public_key, expected_sha256=args.expected_public_key_sha256,
            )
            if len(public) != 32:
                raise ValueError("invalid raw public key bytes")
            if args.pin_action == "enroll":
                result = ledger.enroll(
                    source_name=args.source_name, source_edition=args.source_edition,
                    pin_sha256=args.expected_public_key_sha256,
                    operator_ref=args.operator_ref, verification_ref=args.verification_ref,
                    confirm_pin_sha256=args.confirm_new_sha256,
                )
            else:
                result = ledger.rotate(
                    source_name=args.source_name, source_edition=args.source_edition,
                    prior_sha256=args.confirm_prior_sha256,
                    new_pin_sha256=args.expected_public_key_sha256,
                    operator_ref=args.operator_ref, verification_ref=args.verification_ref,
                    confirm_prior_sha256=args.confirm_prior_sha256,
                    confirm_new_sha256=args.confirm_new_sha256,
                )
        else:
            result = ledger.revoke(
                source_name=args.source_name, source_edition=args.source_edition,
                pin_sha256=args.confirm_prior_sha256,
                operator_ref=args.operator_ref, verification_ref=args.verification_ref,
                confirm_pin_sha256=args.confirm_prior_sha256,
            )
    else:
        host = B14OperatorTrustedDelivery(
            trust_ledger_path=args.trust_ledger,
            public_key_path=args.pinned_public_key,
            expected_public_key_sha256=args.expected_public_key_sha256,
            construction_dir=args.construction_dir,
            native_data_dir=args.native_data_dir,
            observed_journal_path=args.observed_journal,
            lane_handoff_id=args.lane_id, opening_id=args.opening_id,
            job_id=args.job_id, confirm_source_job=args.confirm_source_job,
        )
        if args.native_action == "prepare":
            result = {"request_id": host.prepare(
                goal_id=args.goal_id, candidate_id=args.candidate_id,
                route=tuple(args.route_node),
            ), "private_key_loaded": False, "local_pass_emitted": False}
        elif args.native_action == "signing-request":
            result = host.signing_request(args.request_id)
        else:
            event = host.deliver(
                request_id=args.request_id,
                confirm_request=args.confirm_request,
                approved=args.approve_native_delivery,
                signed_envelope=load_signed_envelope(args.signed_envelope),
            )
            result = {"request_id": event.handoff_id, "event_id": event.event_id,
                      "state": host.host.b12.bridge.projection(event.handoff_id)["state"],
                      "whole_route_verified": False, "native_B3_reexecuted": False,
                      "private_key_loaded": False}
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
