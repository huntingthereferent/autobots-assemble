from __future__ import annotations

from runtime.orchestrator import SystemBinding, SystemEmission

from .factory import FactorySystem
from .personal_operations import PersonalOperationsStore


def factory_binding(
    factory: FactorySystem,
    *,
    order_ids: tuple[str, ...] | None = None,
) -> SystemBinding:
    def emit_ready():
        emissions = []
        current_ids = (
            order_ids
            if order_ids is not None
            else tuple(order.order_id for order in factory.orders())
        )
        for order_id in current_ids:
            order = factory.order(order_id)
            if order.status == "complete":
                continue
            if order.status not in {"open"} and not order.pending_handoff_id:
                continue
            handoff = (
                factory.pending_handoff(order_id)
                if order.pending_handoff_id
                else factory.next_handoff(order_id)
            )
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



def online_school_binding(
    *,
    task_provider,
    task_to_handoff,
    apply_patch,
) -> SystemBinding:
    """Bind Online School's existing local task model to the shared runtime.

    The binding intentionally receives the school's own provider/adapter/patch
    functions instead of importing or replacing its local schema.
    """

    def emit_ready():
        emissions = []
        for task in task_provider():
            if str(task.get("status") or "todo") == "done":
                continue
            handoff = task_to_handoff(task)
            emissions.append(
                SystemEmission(
                    system_id="online-school",
                    local_ref=str(task["id"]),
                    handoff=handoff,
                )
            )
        return tuple(emissions)

    def reconcile(emission, state):
        apply_patch(emission.local_ref, state)

    return SystemBinding(
        system_id="online-school",
        emit_ready=emit_ready,
        reconcile=reconcile,
    )
