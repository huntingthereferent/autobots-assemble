# WORLD Trial15 — body support changes the finite relation

The original WORLD15 source tests two bounded virtual bodies, a disc and an
axis-aligned square whose orientation is **fixed by a declared constraint**.
Both use the original **frictionless translational reflection** contact law,
not separate new physics engines. The square's support function depends on
its normal and can make a different finite face location and contact time.

The original source commit
`65339494abaccac3c4dd20aa89439af057ec3035`
and its independently implemented geometric oracle verify eight completed
two-contact virtual paths, one for each body × controlled source angle.
Only after the first modeled impact is the receiver's orientation and
placement derived from the body's outgoing motion. The second modeled
contact and each finite sample are separately checked in the original
source environment.

A ninth original control, a fixed square at a 30-degree input source
angle, is not admitted by the finite interior-contact model. The source
does not solve the possible finite endpoint response and **does not call
this a physical miss**. Its receiver, contacts and completed frames are
all absent. The A/B adapter preserves that exact refusal rather than
inventing continued motion or a created receiver.

The source-specific adapter carries each completed case into a separate
bounded A/B ledger. The initial input face and virtual moving body exist
first. A modeled contact must be recorded *before* introducing the
movement-derived receiver, which is immediately related to the outgoing
source movement. Only then can a second modeled contact be observed. The
fixed square's rotation constraint remains attached to every revised
movement state: **no free square angular motion is inferred**.

All nine receipt heads and their original source digests are tied in an
ordered manifest. Source-native tests independently check support-plane
geometry, original Trial14 disc limit, finite endpoints, nonpenetration
and contact ancestry. The separate A/B ledger verifier checks recorded
object/relationship history, not source physics or hardware.

This is a bounded mathematical construction experiment. It does not
establish Earth-material behavior, arbitrary rigid-body dynamics,
an endpoint collision response, NIH material blueprint equivalence,
a renderer or a universal set of future WORLD laws. Source WORLD Trials,
ARC, NIH, W13, World48, general A/B construction and All Rights Reserved
licensing remain unchanged.
