from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FactoryOrder:
    order_id: str
    product: str
    quantity: int
    material: str
    stage_index: int = 0
    status: str = "open"
    local_state: dict[str, Any] = field(default_factory=dict)
    pending_handoff_id: str = ""

    def __post_init__(self) -> None:
        if not self.order_id.strip():
            raise ValueError("order_id is required")
        if not self.product.strip():
            raise ValueError("product is required")
        if not self.material.strip():
            raise ValueError("material is required")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
