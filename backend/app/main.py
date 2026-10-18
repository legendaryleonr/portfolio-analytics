
from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Portfolio Analytics API")


# Describe what a transaction should look like
class Transaction(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    transaction_type: Literal["BUY", "SELL"]
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    trade_date: date


# Temporary storage (we'll use PostgreSQL later)
transactions: list[Transaction] = []


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/transactions", status_code=201)
def add_transaction(transaction: Transaction):
    transactions.append(transaction)

    return {
        "message": "Transaction added successfully",
        "transaction": transaction,
        "total_transactions": len(transactions),
    }


@app.get("/transactions")
def get_transactions():
    return transactions
