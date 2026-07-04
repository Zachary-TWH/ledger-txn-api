import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.main import get_db

# Use a separate test database so tests don't touch your real data
TEST_DATABASE_URL = "postgresql://postgres:mysecret@localhost:5432/ledger_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use test database instead of production database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# TestClient wraps our FastAPI app — lets us make requests without running the server
client = TestClient(app)

# This runs before every test — creates fresh tables
# After every test — drops them, so each test starts clean
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ── TESTS ──────────────────────────────────────────────────────────────────────

def test_create_account():
    response = client.post("/accounts", json={"owner_name": "Alice", "currency": "USD"})
    assert response.status_code == 200
    data = response.json()
    assert data["owner_name"] == "Alice"
    assert data["balance"] == 0.0

def test_deposit():     
    # create account first
    account = client.post("/accounts", json={"owner_name": "Alice", "currency": "USD"}).json()
    # create EXTERNAL account (required by deposit logic)
    client.post("/accounts", json={"owner_name": "EXTERNAL", "currency": "USD"})

    response = client.post("/deposit", json={
        "account_id": account["id"],
        "amount": 100,
        "idempotency_key": "dep-001"
    })
    assert response.status_code == 200
    assert response.json()["new_balance"] == 100.0

def test_withdraw_insufficient_funds():
    account = client.post("/accounts", json={"owner_name": "Alice", "currency": "USD"}).json()
    client.post("/accounts", json={"owner_name": "EXTERNAL", "currency": "USD"})

    response = client.post("/withdraw", json={
        "account_id": account["id"],
        "amount": 100,
        "idempotency_key": "wdr-001"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"

def test_transfer():
    alice = client.post("/accounts", json={"owner_name": "Alice", "currency": "USD"}).json()
    bob = client.post("/accounts", json={"owner_name": "Bob", "currency": "USD"}).json()
    client.post("/accounts", json={"owner_name": "EXTERNAL", "currency": "USD"})

    # deposit into alice first
    client.post("/deposit", json={
        "account_id": alice["id"],
        "amount": 100,
        "idempotency_key": "dep-001"
    })

    response = client.post("/transfer", json={
        "from_account_id": alice["id"],
        "to_account_id": bob["id"],
        "amount": 40,
        "idempotency_key": "txn-001"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["from_account_new_balance"] == 60.0
    assert data["to_account_new_balance"] == 40.0

def test_transfer_same_account():
    alice = client.post("/accounts", json={"owner_name": "Alice", "currency": "USD"}).json()
    response = client.post("/transfer", json={
        "from_account_id": alice["id"],
        "to_account_id": alice["id"],
        "amount": 10,
        "idempotency_key": "txn-002"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot transfer to the same account"