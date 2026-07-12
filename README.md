# double-entry-ledger

A REST API for a double-entry bookkeeping ledger, built with FastAPI and PostgreSQL. Designed to mirror the kind of financial transaction system you'd find at a crypto exchange or fintech backend.

Built this to learn backend engineering properly — every design decision was made deliberately, not just copied from a tutorial.

## What it does

- Create accounts and move money between them (deposit, withdraw, transfer)
- Every transaction creates two ledger entries (debit + credit) that must balance — the core double-entry principle
- Idempotency on all write operations — safe to retry without double-processing
- JWT authentication on all endpoints
- Row-level locking on balance updates to prevent race conditions under concurrent load
- Balance integrity check — recomputes balance from ledger entries and flags any discrepancy

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic (migrations)
- Docker + Docker Compose
- pytest

## Running locally

```bash
docker compose up --build -d
docker compose exec api sh -c "alembic upgrade head"
```

API available at `http://localhost:8000`.

## Usage

Register and login to get a token:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'

curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```

Include the token in subsequent requests:
```bash
curl -X POST http://localhost:8000/accounts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"owner_name": "Alice", "currency": "USD"}'
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /register | Create a user |
| POST | /login | Get JWT token |
| POST | /accounts | Create an account |
| POST | /deposit | Deposit funds |
| POST | /withdraw | Withdraw funds |
| POST | /transfer | Transfer between accounts |
| GET | /accounts/{id} | Get account balance |
| GET | /accounts/{id}/transactions | Transaction history (paginated) |
| GET | /accounts/{id}/integrity | Verify balance against ledger entries |

## Design decisions worth noting

**Why double-entry?** Every money movement creates two ledger entries — a debit on one account and a credit on another. The ledger entries are the source of truth; the stored balance is a cache that gets verified against them.

**Why idempotency keys?** Network retries are a reality. A client that doesn't hear back from the server might retry a deposit — without idempotency, that's a double deposit. The key is enforced unique at the database level, not application level.

**Why row-level locking?** Two concurrent deposits hitting the same account would both read the same balance, add to it, and write back — one deposit would be lost. `SELECT FOR UPDATE` serializes access to the row. Transfer locks both accounts in consistent ID order to prevent deadlocks.

## Running tests

```bash
pytest test_main.py -v
```

Tests run against a separate `ledger_test` database and wipe themselves clean after each test.
