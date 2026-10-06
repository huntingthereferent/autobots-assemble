from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

from runtime import Handoff, HandoffState

from .model import FactoryOrder


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


STAGES = (
    {
        "name": "supply",
        "actor": "supplier-sim",
        "relation": "supply material",
        "witness": "material supplied",
        "evidence": ("simulation", "supplier_record", "human_report"),
    },
    {
        "name": "machine",
        "actor": "machine-sim",
        "relation": "machine feature",
        "witness": "machining operation completed",
        "evidence": ("simulation", "machine_telemetry"),
    },
    {
        "name": "inspect",
        "actor": "inspection-sim",
        "relation": "inspect output",
        "witness": "inspection completed",
        "evidence": ("simulation", "measurement", "inspection_record"),
    },
    {
        "name": "assemble",
        "actor": "assembly-sim",
        "relation": "assemble product",
        "witness": "assembly completed",
        "evidence": ("simulation", "machine_telemetry", "human_report"),
    },
    {
        "name": "ship",
        "actor": "shipping-sim",
        "relation": "ship product",
        "witness": "shipment recorded",
        "evidence": ("simulation", "carrier_record", "human_report"),
    },
)


class FactorySystem:
    """Factory-local order state that emits shared handoffs.

    The factory owns order/stage state. The runtime owns live handoff execution.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._orders: dict[str, FactoryOrder] = {}
        self._events: list[dict[str, Any]] = []

        if self.path and self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    event = json.loads(line)
                    self._events.append(event)
                    self._replay(event)

    def _append(self, event_type: str, payload: dict[str, Any]) -> None:
        event = {
            "event_type": event_type,
            "occurred_at": utc_now(),
            "payload": payload,
        }
        self._events.append(event)
        self._replay(event)

        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _replay(self, event: dict[str, Any]) -> None:
        kind = event["event_type"]
        payload = event["payload"]

        if kind == "ORDER_CREATED":
            self._orders[payload["order_id"]] = FactoryOrder(**payload)
            return

        if kind == "HANDOFF_EMITTED":
            order = self._orders[payload["order_id"]]
            self._orders[order.order_id] = replace(
                order,
                pending_handoff_id=payload["handoff_id"],
            )
            return

        if kind == "HANDOFF_RECONCILED":
            order = self._orders[payload["order_id"]]
            if payload["status"] == "COMPLETE":
                next_stage = order.stage_index + 1
                complete = next_stage >= len(STAGES)
                self._orders[order.order_id] = replace(
                    order,
                    stage_index=next_stage,
                    status="complete" if complete else "open",
                    local_state=dict(payload.get("local_state") or {}),
                    pending_handoff_id="",
                )
            else:
                self._orders[order.order_id] = replace(
                    order,
                    status=str(payload["status"]).lower(),
                    pending_handoff_id="",
                )

    def create_order(
        self,
        *,
        order_id: str,
        product: str,
        quantity: int,
        material: str,
    ) -> FactoryOrder:
        if order_id in self._orders:
            raise ValueError(f"order already exists: {order_id}")
        order = FactoryOrder(
            order_id=order_id,
            product=product,
            quantity=quantity,
            material=material,
            local_state={
                "order": order_id,
                "product": product,
                "quantity": quantity,
                "material": material,
            },
        )
        self._append("ORDER_CREATED", asdict(order))
        return self.order(order_id)

    def order(self, order_id: str) -> FactoryOrder:
        return self._orders[order_id]

    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)

    def _stage_inputs(self, order: FactoryOrder) -> dict[str, Any]:
        state = order.local_state
        stage = STAGES[order.stage_index]["name"]

        if stage == "supply":
            return {
                "order": order.order_id,
                "material": order.material,
                "quantity": order.quantity,
            }
        if stage == "machine":
            return {
                "order": order.order_id,
                "product": order.product,
                "material": state["material"],
                "quantity": state["quantity"],
                "material_state": state["material_state"],
            }
        if stage == "inspect":
            return {
                "order": order.order_id,
                "product": order.product,
                "part": state["part"],
                "quantity": state["quantity"],
                "part_state": state["part_state"],
            }
        if stage == "assemble":
            return {
                "order": order.order_id,
                "product": order.product,
                "quantity": state["accepted"],
                "inspection_state": state["inspection_state"],
            }
        if stage == "ship":
            return {
                "order": order.order_id,
                "product": order.product,
                "quantity": state["quantity"],
                "product_state": state["product_state"],
            }
        raise ValueError(f"unknown factory stage: {stage}")

    def _build_handoff(
        self,
        order: FactoryOrder,
        *,
        handoff_id: str,
    ) -> Handoff:
        if order.stage_index >= len(STAGES):
            raise ValueError(f"order {order.order_id} has no remaining stage")
        stage = STAGES[order.stage_index]
        return Handoff(
            handoff_id=handoff_id,
            referent=f"{order.order_id} / {order.product}",
            from_actor="factory-system",
            to_actor=stage["actor"],
            required_relation=stage["relation"],
            inputs=self._stage_inputs(order),
            expected_output={"stage": stage["name"], "state_change": True},
            required_witnesses=(stage["witness"],),
            admissible_evidence={
                stage["witness"]: tuple(stage["evidence"]),
            },
            boundaries=(
                "Simulation evidence must remain marked simulated.",
                "A completed stage does not establish later stages.",
            ),
            provenance=(
                f"factory-order:{order.order_id}",
                f"factory-stage:{stage['name']}",
            ),
            metadata={
                "source_system": "factory",
                "order_id": order.order_id,
                "stage": stage["name"],
                "title": f"{order.order_id} — {stage['name']}",
            },
        )
    def pending_handoff(self, order_id: str) -> Handoff | None:
        """Reconstruct an already-emitted handoff without emitting it again."""
        order = self.order(order_id)
        if not order.pending_handoff_id:
            return None
        return self._build_handoff(
            order,
            handoff_id=order.pending_handoff_id,
        )

    def next_handoff(self, order_id: str) -> Handoff | None:
        order = self.order(order_id)
        if order.status == "complete":
            return None
        if order.pending_handoff_id:
            raise ValueError(
                f"order {order_id} is awaiting {order.pending_handoff_id}"
            )
        if order.stage_index >= len(STAGES):
            return None

        stage = STAGES[order.stage_index]
        handoff_id = (
            f"factory-{order.order_id}-{order.stage_index + 1:02d}-{stage['name']}"
        )
        handoff = self._build_handoff(order, handoff_id=handoff_id)
        self._append(
            "HANDOFF_EMITTED",
            {
                "order_id": order.order_id,
                "handoff_id": handoff.handoff_id,
                "stage": stage["name"],
            },
        )
        return handoff

    def reconcile(
        self,
        order_id: str,
        *,
        handoff: Handoff,
        state: HandoffState,
    ) -> FactoryOrder:
        order = self.order(order_id)
        if order.pending_handoff_id != handoff.handoff_id:
            raise ValueError(
                f"{handoff.handoff_id} is not the pending handoff for {order_id}"
            )

        merged = dict(order.local_state)
        if state.status == "COMPLETE":
            merged.update(state.output)

        self._append(
            "HANDOFF_RECONCILED",
            {
                "order_id": order_id,
                "handoff_id": handoff.handoff_id,
                "status": state.status,
                "local_state": merged,
                "evidence": [
                    {
                        "condition": item.condition,
                        "kind": item.kind,
                        "source": item.source,
                        "ref": item.ref,
                        "depth": item.depth,
                    }
                    for item in state.evidence
                ],
            },
        )
        return self.order(order_id)
