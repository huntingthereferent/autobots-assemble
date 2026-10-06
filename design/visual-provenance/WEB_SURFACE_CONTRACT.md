# Web Surface Contract

A website surface is not allowed to acquire visual structure accidentally.

For every durable working surface, preserve these relations explicitly:

```text
PURPOSE
what this surface exists to let someone do

ENTRANCE / NAVIGATION
how the user reaches the working relation

WORKSPACE
the controls, inputs, state, and actions required to move it

OUTPUT / ARTIFACT
the thing produced, changed, inspected, or returned

VISUAL PROVENANCE
the approved visual grammar that constrains presentation

LOCAL DOMAIN
the product/system-specific relations that the visual template must not erase
```

## Required website/app files

A surface that has an approved visual template should carry a local
`visual-provenance.json` binding.

The binding does not own the template. It points to the template registry and
records local preservation/additions/deviations.

When a site has multiple substantially different visual layers, use one binding
per surface in a `visual-provenance/` directory instead of forcing the whole
site into one template.

Example:

```text
app/
  index.html
  worksheet.html
  visual-provenance/
    dashboard.json
    worksheet-studio.json
```

A single-surface or early application may use:

```text
app/
  visual-provenance.json
```

## Implementation rule

The HTML surface should identify its visual template:

```html
<meta name="visual-template" content="notegpt_math_generator_v1">
```

That marker is not styling. It creates an inspectable relation from rendered
surface back to the repository's visual provenance.

## Review rule

When a surface starts to look generic, inconsistent, or "AI-made":

1. inspect the current surface binding;
2. inspect its approved template;
3. compare the implementation against the preserved grammar;
4. record a deliberate deviation if the local system genuinely requires one;
5. otherwise correct the implementation rather than inventing a new aesthetic.

Do not create a new visual template merely because implementation drift occurred.

## Template discovery

When a useful external or internal visual witness is encountered:

```text
capture source + date
→ describe what is visually doing work
→ remove brand-specific/copied details
→ record reusable grammar
→ mark candidate
→ bind to a real surface and test
→ approve when the grammar survives translation
```

This lets the repository accumulate visual capability without accumulating
random style fragments.
