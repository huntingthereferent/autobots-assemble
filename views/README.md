# Views

`views/` contains read-only or generated projections over preserved state/evidence.

A view may change representation, audience, or aggregation. It may not mutate the underlying evidence or upgrade what was demonstrated.

Human-language interpretation/rendering belongs in `language/`.

Capability/resume/credibility summaries belong here or beside their source evidence when tightly scoped.

The former generic `lenses/` package was removed because its responsibilities are now covered by these explicit layers.
