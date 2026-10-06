from __future__ import annotations

from runtime.orchestrator import SystemBinding, SystemEmission

from .factory import FactorySystem
from .personal_operations import PersonalOperationsStore


def factory_binding(
    factory: FactorySystem,
    *,
    order_ids: tuple[str, ...],
) -> SystemBinding:
    def emit_ready():
        emissions = []
        for order_id in order_ids:
            order = factory.order(order_id)
            if order.status == "complete" or order.pending_handoff_id:
                continue
            handoff = factory.next_handoff(order_id)
            if handoff is not None:
                emissions.append(
                    SystemEmission(
                        system_id="factory",
                        local_ref=order_id,
                        handoff=handoff,
                    )
                )
        return tuple(emissions)

    def reconcile(emission, state):
        factory.reconcile(
            emission.local_ref,
            handoff=emission.handoff,
            state=state,
        )

    return SystemBinding(
        system_id="factory",
        emit_ready=emit_ready,
        reconcile=reconcile,
    )


def personal_operations_binding(
    personal: PersonalOperationsStore,
) -> SystemBinding:
    def emit_ready():
        emissions = []
        for task in personal.tasks():
            if personal.admitted_handoff_id(task.task_id) is None:
                continue
            if personal.task_result(task.task_id) is not None:
                continue
            handoff = personal.admitted_handoff(task.task_id)
            emissions.append(
                SystemEmission(
                    system_id="personal-operations",
                    local_ref=task.task_id,
                    handoff=handoff,
                )
            )
        return tuple(emissions)

    def reconcile(emission, state):
        personal.reconcile_task_result(emission.local_ref, state)

    return SystemBinding(
        system_id="personal-operations",
        emit_ready=emit_ready,
        reconcile=reconcile,
    )
