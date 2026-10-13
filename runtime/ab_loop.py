"""Legacy import path for referent traversal.

The historical A/B module path remains valid for existing clients and tests.
New code should import from `runtime.referent_traversal`.
"""
from .referent_traversal import *

ABResultState = ReferentResultState
ABLoopResult = ReferentTraversalResult
ABFrame = ReferentFrame
ABMove = ReferentMove
ABAgent = ReferentAgent
ABStep = ReferentStep
ABLoop = ReferentTraversal
