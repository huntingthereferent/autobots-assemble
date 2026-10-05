# Application Security Lab — Evidence Build

## Referent

Build one inspectable application-security witness over an owned/local target.

This project is not a penetration-testing exercise against third-party systems. It exists to prove a complete security-engineering movement:

**asset / trust boundary → threat → vulnerable behavior → detection → remediation → regression**

## First vulnerability class

OWASP-style injection weakness in a local SQLite-backed lookup function.

The project preserves both states:

- `vulnerable.py` contains the intentionally unsafe implementation.
- `secure.py` contains the remediated parameterized implementation.

The vulnerable implementation remains only as a controlled regression fixture so the evidence can show what changed and why.

## Threat boundary

Asset:
- local user records in SQLite.

Trust boundary:
- untrusted lookup input crosses into a database query.

Threat:
- attacker-controlled input changes query structure rather than remaining data.

Expected control:
- parameterized SQL statement keeps input in a value position.

## Acceptance

- local fixture proves normal lookup behavior;
- controlled injection input broadens results in the intentionally vulnerable implementation;
- the same input does not broaden results after remediation;
- secure lookup still supports valid user lookup;
- a machine-readable security report records finding, control, before-state, after-state, and evidence;
- automated tests keep the repaired state from regressing;
- clean GitHub Actions run passes.

## Boundary

Passing this closes a first **Cybersecurity / Application Security** witness.

It does not claim:
- third-party penetration testing;
- red-team operations;
- network exploitation;
- production security operations;
- broad OWASP coverage beyond the demonstrated class.
