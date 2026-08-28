# double-entry-ledger

A REST API for a double-entry bookkeeping ledger, built with FastAPI and PostgreSQL. Designed to mirror the kind of financial transaction system you'd find at a crypto exchange or fintech backend.

Built this to learn backend engineering properly — every design decision was made deliberately, not just copied from a tutorial.

## What it does

- Create accounts and move money between them (deposit, withdraw, transfer)
- Every transaction creates two ledger entries (debit + credit) that must balance — the core double-entry principle
- Idempotency on all write operations — safe to retry without double-processing
- JWT access tokens + long-lived refresh tokens, with server-side revocation on logout
- Row-level locking on balance updates to prevent race conditions under concurrent load
- Currency mismatch protection — transfers between accounts in different currencies are rejected
- Rate limiting on every endpoint to guard against abuse
- Balance integrity check — recomputes balance from ledger entries and flags any discrepancy, both on demand (endpoint) and automatically (background job every minute)
- Redis caching on account lookups to reduce database load, with a short TTL

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic (migrations)
- python-jose (JWT) + passlib/bcrypt (password hashing)
- slowapi (rate limiting)
- APScheduler (background reconciliation job)
- Docker + Docker Compose
- pytest
- Redis (caching)

## Running locally

```bash
docker compose up --build -d
docker compose exec api sh -c "alembic upgrade head"
```

API available at `http://localhost:8000`.

Redis starts automatically as part of `docker compose up` — no separate setup needed.

## Usage

Register and login to get a token pair:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'

curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```
Login returns an `access_token` (30 min expiry) and a `refresh_token` (7 day expiry, stored server-side so it can be revoked).

Include the access token in subsequent requests:
```bash
curl -X POST http://localhost:8000/accounts \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"owner_name": "Alice", "currency": "USD"}'
```

When the access token expires, use the refresh token to get a new one without logging in again:
```bash
curl -X POST http://localhost:8000/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /register | Create a user |
| POST | /login | Get access + refresh token pair |
| POST | /refresh | Exchange a valid refresh token for a new access token |
| POST | /logout | Revoke a refresh token |
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

**Why refresh tokens?** Short-lived access tokens limit the damage if one leaks, but forcing a re-login every 30 minutes is bad UX. The refresh token is a random string (not a JWT) stored in the database, so it can be revoked on logout — a stateless JWT alone can't be invalidated before it expires.

**Why a background reconciliation job?** The `/integrity` endpoint checks one account on demand, but nobody's going to call it constantly. A scheduled job sweeps every account each minute and logs a warning if computed balance ever drifts from stored balance, so a bug would surface in the logs instead of silently corrupting data.

## Running tests

```bash
pytest test_main.py -v
```

Tests run against a separate `ledger_test` database and wipe themselves clean after each test.

## Known limitations

- `SECRET_KEY` is hardcoded in `main.py` — fine for local dev, needs to move to an environment variable before this touches anything real.
- `/dev-setup` is a convenience endpoint for quickly creating an EXTERNAL + test account locally — not meant to exist in a production build.
- Account balance caching has a stale-read window: after a deposit/withdraw/transfer, `GET /accounts/{id}` can return the pre-update balance for up to 30 seconds (the cache TTL) if it was already cached. Cache invalidation on write isn't implemented yet.