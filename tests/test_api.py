import pytest
from fastapi.testclient import TestClient
from app.main import app, accounts

client = TestClient(app)

@pytest.fixture
def reset_accounts(): 
    original = accounts.copy()

    accounts.clear()
    accounts.update({
        101: 5000, 
        102: 2000, 
        103: 1000
    })

    yield 

    accounts.clear()
    accounts.update(original)

@pytest.mark.parametrize("amount, expected_status", [(-100, 400), (0, 400)])
def test_invalid_deposit(reset_accounts, amount, expected_status): 
    before = accounts.copy()
    response = client.post("/accounts/101/deposit", json={"amount": amount})

    assert response.status_code == expected_status
    assert response.json()["detail"] == "Invalid amount"
    assert before == accounts

def test_deposit_positive_amount(reset_accounts): 
    before = client.get("/accounts/101")
    balance_before = before.json()["balance"]

    response = client.post(
        "/accounts/101/deposit", 
        json={"amount": 50}
    )

    assert response.status_code == 200
    assert response.json()["balance"] == balance_before + 50

def test_account_balance(reset_accounts): 
    response = client.get("/accounts/101")

    assert response.status_code == 200
    assert response.json()["balance"] == 5000

def test_deposit_nonexistent_account(reset_accounts): 
    before = accounts.copy()

    response = client.post("/accounts/901/deposit", json={"amount": 200})

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"
    assert 901 not in accounts
    assert before == accounts

def test_withdraw_success(reset_accounts): 
    consult = client.get("/accounts/101")
    balance_before = consult.json()["balance"]
    
    response = client.post("/accounts/101/withdraw", json={"amount": 200})

    assert response.status_code == 200
    assert response.json()["balance"] == balance_before - 200

def test_withdraw_inssufficient_funds(reset_accounts):
    before = accounts.copy() 
    response = client.post("/accounts/101/withdraw", json={"amount": 6000})

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"
    assert before == accounts

def test_withdraw_exact_balance(reset_accounts): 
    response = client.post("/accounts/101/withdraw", json={"amount": 5000})

    assert response.status_code == 200
    assert response.json()["balance"] == 0
    assert client.get("/accounts/101").json()["balance"] == 0

def test_withdraw_negative_amount(reset_accounts):
    before = accounts.copy() 
    response = client.post("/accounts/101/withdraw", json={"amount": -100})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid amount"
    assert before == accounts

def test_withdraw_zero_amount(reset_accounts): 
    before = accounts.copy() 
    response = client.post("/accounts/101/withdraw", json={"amount": 0})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid amount"
    assert before == accounts

def test_transfer_success(reset_accounts): 
    before = accounts.copy()
    response = client.post("/accounts/101/transfer", json={"destination_id": 102, "amount": 500})

    assert response.status_code == 200
    assert (before[101] - 500) == accounts[101]
    assert (before[102] + 500) == accounts[102]
    assert response.json()["source_balance"] == accounts[101]
    assert response.json()["destination_balance"] == accounts[102]
    assert sum(before.values()) == sum(accounts.values())

def test_transfer_insufficient_funds(reset_accounts): 
    before = accounts.copy()
    response = client.post("/accounts/101/transfer", json={"destination_id": 102, "amount": 6000})

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"
    assert before == accounts

@pytest.mark.parametrize("source_id, destination_id, expected_status, expected_detail", [(101, 999, 404, "Account not found"), (101, 101, 400,"Cannot transfer to same account"), (999, 102, 404,"Account not found")])
def test_invalid_transfer(reset_accounts, source_id, destination_id, expected_status, expected_detail): 
    before = accounts.copy()
    response = client.post(f"/accounts/{source_id}/transfer", json={"destination_id": destination_id, "amount": 500})

    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail
    assert before == accounts