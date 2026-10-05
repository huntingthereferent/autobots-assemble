# Threat Model — SQL Query Boundary

## Asset

Local `users` records, including the administrative role record.

## Entry point

A username string accepted by a lookup function.

## Trust boundary

The username is untrusted data. The SQLite query is trusted code.

The boundary fails when input text is inserted into the SQL statement itself.

## Threat

An input containing SQL syntax can alter the statement's predicate and broaden the result set.

The controlled regression value is used only against the project's in-memory SQLite fixture.

## Before

```text
untrusted input
  ↓
string interpolation
  ↓
SQL text changes
  ↓
unexpected records returned
```

## Control

Parameter binding:

```text
untrusted input
  ↓
bound SQL parameter
  ↓
query structure remains fixed
  ↓
input is treated as a value
```

## Verification

The acceptance suite requires all three relations:

1. ordinary lookup still works;
2. the intentionally vulnerable fixture demonstrates the failure;
3. the remediated implementation returns zero rows for the controlled injection string.

The vulnerable implementation is retained as a local before-state witness only.
