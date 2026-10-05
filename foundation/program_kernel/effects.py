from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class EffectError(RuntimeError):
    pass


@dataclass(frozen=True)
class EffectCall:
    effect: str
    adapter: str
    args_count: int
    kwargs: list[str]
    result_type: str


class PortContext:
    def __init__(
        self,
        declared: set[str],
        adapters: dict[str, Callable[..., Any]],
        calls: list[EffectCall],
    ) -> None:
        self._declared = declared
        self._adapters = adapters
        self._calls = calls

    def call(self, effect: str, *args: Any, **kwargs: Any) -> Any:
        if effect not in self._declared:
            raise EffectError(f"effect not declared by operation: {effect}")
        if effect not in self._adapters:
            raise EffectError(f"effect not admitted for execution: {effect}")

        adapter = self._adapters[effect]
        result = adapter(*args, **kwargs)
        name = getattr(adapter, "__qualname__", getattr(adapter, "__name__", type(adapter).__name__))
        self._calls.append(
            EffectCall(
                effect=effect,
                adapter=name,
                args_count=len(args),
                kwargs=sorted(kwargs),
                result_type=type(result).__name__,
            )
        )
        return result
