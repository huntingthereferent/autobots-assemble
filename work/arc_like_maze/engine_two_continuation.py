"""Compatibility import for earlier serialized B-action continuation callers."""
from .cyclic_action_continuation import *  # noqa: F401,F403
EngineTwoContinuationKernel = CyclicActionContinuation
