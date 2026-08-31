# double-entry-ledger

A REST API for a double-entry bookkeeping ledger, built with FastAPI and PostgreSQL. Designed to mirror the kind of financial transaction system you'd find at a crypto exchange or fintech backend.

Built this to learn backend engineering properly. Every design decision was made deliberately, not just copied from a tutorial.

## What it does

- Create accounts and move money between them (deposit, withdraw, transfer)
- Every transaction creates two ledger entries (debit and credit) that must balance, the core double-entry principle
- Idempotency on all write operations, safe to retry without double-processing
- JWT access tokens plus long-lived refresh tokens, with server-side revocation on logout
- Row-level locking on balance updates to prevent race conditions under concurrent load
- Currency mismatch protection, transfers between accounts in different currencies are rejected
- Rate limiting on every endpoint to guard against abuse
- Balance integrity check, recomputes balance from ledger entries and flags any discrepancy, both on demand (endpoint) and automatically (background job every minute)
- Redis caching on account lookups to reduce database load, with cache invalidation on writes so balances never go stale after a deposit, withdrawal, or transfer
- Background jobs (reconciliation and exchange rate fetching) run on a message queue instead of inside the API process, so they don't compete with API requests for resources and can be scaled independently
- Reconciliation and exchange rate fetching run on a schedule automatically, with retry logic on the exchange rate fetch in case the external API call fails

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic (migrations)
- python-jose (JWT) and passlib/bcrypt (password hashing)
- slowapi (rate limiting)
- Redis (caching)
- RabbitMQ (message queue)
- Celery (background workers)
- Celery Beat (job scheduling)
- Docker and Docker Compose
- pytest

## Running locally

```bash
docker compose up --build -d
docker compose exec api sh -c "alembic upgrade head"
```

API available at `http://localhost:8000`.

Redis, RabbitMQ, the Celery worker, and the Celery beat scheduler all start automatically as part of `docker compose up`. No separate setup needed.

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
Login returns an `access_token` (30 min expiry) and a `refresh_token` (7 day expiry, stored server side so it can be revoked).

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
| POST | /login | Get access and refresh token pair |
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

**Why double-entry?** Every money movement creates two ledger entries, a debit on one account and a credit on another. The ledger entries are the source of truth, the stored balance is a cache that gets verified against them.

**Why idempotency keys?** Network retries are a reality. A client that doesn't hear back from the server might retry a deposit. Without idempotency, that's a double deposit. The key is enforced unique at the database level, not the application level.

**Why row level locking?** Two concurrent deposits hitting the same account would both read the same balance, add to it, and write back, so one deposit would be lost. `SELECT FOR UPDATE` serializes access to the row. Transfer locks both accounts in consistent ID order to prevent deadlocks.

**Why refresh tokens?** Short lived access tokens limit the damage if one leaks, but forcing a re-login every 30 minutes is bad UX. The refresh token is a random string, not a JWT, stored in the database so it can be revoked on logout. A stateless JWT alone can't be invalidated before it expires.

**Why a background reconciliation job?** The `/integrity` endpoint checks one account on demand, but nobody's going to call it constantly. A scheduled job sweeps every account each minute and logs a warning if computed balance ever drifts from stored balance, so a bug would surface in the logs instead of silently corrupting data.

**Why a message queue instead of running background jobs inside the API?** Reconciliation and exchange rate fetching used to run on a timer inside the API process itself. That works fine until a job takes long enough to compete with actual API requests for CPU and memory. Moving them onto a queue means a separate worker process picks up the work. The API stays responsive no matter how long a job takes, and if a job fails it can retry without taking the API down with it.

**Why Celery Beat instead of a simple timer?** Beat's only job is to publish a task to the queue on schedule. It never runs the task itself, the worker does. That separation means you can run several workers pulling from the same queue if you ever need more throughput, but you only ever run one Beat, so scheduled jobs never fire twice.

## Running tests

```bash
pytest test_main.py -v
```

Tests run against a separate `ledger_test` database and wipe themselves clean after each test.

## Known limitations

- `SECRET_KEY` is hardcoded in `main.py`. Fine for local dev, needs to move to an environment variable before this touches anything real.
- `/dev-setup` is a convenience endpoint for quickly creating an EXTERNAL and test account locally. Not meant to exist in a production build.