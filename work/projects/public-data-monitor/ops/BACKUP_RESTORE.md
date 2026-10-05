# PostgreSQL Backup / Restore

The local Docker stack keeps PostgreSQL state in the `pgdata` volume. Operational recovery must not depend on that volume remaining intact.

## Backup

```sh
sh ops/backup.sh platform-backup.sql
```

The dump is produced by the same PostgreSQL 16 container used by the application and includes schema plus data. Ownership and privilege statements are omitted so the dump can be restored into a replacement environment.

## Restore

Start the database service, then restore:

```sh
docker compose up -d db
sh ops/restore.sh platform-backup.sql
```

The restore script uses `ON_ERROR_STOP=1`; a failed statement makes the recovery fail rather than silently producing a partial restore.

## Acceptance witness

CI proves recovery by:

1. creating the application schema;
2. writing a successful source run and durable observation;
3. taking a PostgreSQL dump;
4. destroying the public schema;
5. recreating an empty public schema;
6. restoring the dump;
7. verifying the exact source-run status and observation payload.

This is a database recovery witness for the containerized platform. It does not claim managed RDS snapshot/PITR recovery until an AWS runtime exists.
