from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class DepositRequest(BaseModel): 
    amount: int

class TransferRequest(BaseModel):
    destination_id: int
    amount: int

@app.post("/accounts/{account_id}/transfer")
def transfer(account_id: int, request: TransferRequest):
    if account_id not in accounts: 
        raise HTTPException(status_code=404, detail="Account not found")
    if request.destination_id not in accounts: 
        raise HTTPException(status_code=404, detail="Account not found")
    if request.amount <= 0: 
        raise HTTPException(status_code=400, detail="Invalid amount")
    if request.amount > accounts[account_id]:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    if request.destination_id == account_id: 
        raise HTTPException(status_code=400, detail="Cannot transfer to same account")

    accounts[account_id] -= request.amount
    accounts[request.destination_id] += request.amount

    return{
        "source_id": account_id,
        "destination_id": request.destination_id, 
        "source_balance": accounts[account_id], 
        "destination_balance": accounts[request.destination_id]
    }

accounts = {
    101: 5000, 
    102: 2000, 
    103: 1000
}

@app.get("/")
def home(): 
    return {"message": "Banking API is running"}

@app.get("/accounts/{account_id}")
def get_accounts(account_id: int): 
    if account_id in accounts: 
        return {
            "account_id": account_id, 
            "balance": accounts[account_id]
        }
    raise HTTPException(
        status_code=404, 
        detail="Account not found"
    )

@app.post("/accounts/{account_id}/deposit")
def deposit(account_id: int, request: DepositRequest): 
    if account_id in accounts: 
        amount = request.amount
        if amount > 0: 
            accounts[account_id] += amount
            return {
                "account_id": account_id,
                "balance": accounts[account_id]
            }
        raise HTTPException(
        status_code=400,
        detail="Invalid amount"
    )
    raise HTTPException(
            status_code=404, 
            detail="Account not found"
        )

@app.post("/accounts/{account_id}/withdraw")
def withdraw(account_id: int, request: DepositRequest): 
    if account_id not in accounts: 
        raise HTTPException(status_code=404, detail="Account not found")
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")   
    if accounts[account_id] < request.amount: 
        raise HTTPException(status_code=400, detail="Insufficient funds")
    accounts[account_id] -= request.amount
    return {"account_id": account_id, "balance": accounts[account_id]}