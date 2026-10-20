# Movement 6: attack the previously passing scoped-reference fingerprint

This does **not** claim upstream REA is semantically unsound. Its v3 matcher explicitly labels structural matches as medium-confidence inference. The subject is our own earlier experimental v5 scoped-reference fingerprint, applied to actual pinned REA source.

Check four deliberate false equivalences: named function `.name`, direct eval of an identifier string after a consistent parameter rename, `arguments.callee.name`, and the observable `.name` of an arrow function inferred from its assigned local binding. These strings can change real execution outputs without changing the scoped reference vector. A consistent harmless rename is the positive control, and an assignment target mutation is a separate relation-distinguishing control.

Run native real REA Vitest, preserve source and observed output pairs and typecheck. The next edition must reject these cases or encode the missing observable distinctions; do not discard them, and do not silently rewrite v3.
