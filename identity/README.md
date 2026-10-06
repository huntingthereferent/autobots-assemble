# Identity Continuity

Identity is another continuity boundary.

The hub should not define a person by the social provider they used to enter.

```text
external identity assertion
→ provider subject / durable provider ID
→ linked internal person
→ existing movement / lineage / permissions
→ continue
```

## Rule

One person may have many linked external identities.

Examples:

```text
person_123
├── google:<sub>
├── github:<id>
├── apple:<sub>
└── microsoft:<sub>
```

The provider identity is provenance and an authentication method. It is **not** the canonical person ID.

## Login movement

```text
ARRIVE
→ authenticate with existing provider
→ resolve durable external identity
→ match linked person
→ CONTINUE prior movement
```

If no link exists:

```text
external identity
→ explicit create/link decision
→ internal person
→ preserve provider provenance
```

Do not silently merge accounts from a mutable display name, handle, or unverified email.

## Linking

Linking a second provider should require an already-authenticated person or another explicit verification step.

```text
authenticated person
+ new provider assertion
→ LINK
→ same internal person
```

Unlinking removes an authentication path; it must not erase the person's movement history.

## Movement boundary

Authentication answers **who is entering**.

It must not:

- flatten provider identities into separate people;
- turn provider profile data into authority over local state;
- copy provider passwords into the hub;
- use provider handles as durable identity;
- erase prior movement when the login method changes.

## Recommended first providers

- Google
- Apple
- GitHub
- Microsoft

Other providers can enter through the same external-identity contract where supported.
