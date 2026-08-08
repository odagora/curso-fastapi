from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from models import Customer, Transaction, TransactionCreate
from db import SessionDep

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_data: TransactionCreate, session: SessionDep):
    customer = session.get(Customer, transaction_data.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist"
        )

    transaction = Transaction.model_validate(transaction_data)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get("", response_model=list[Transaction])
async def list_transactions(session: SessionDep):
    return session.exec(select(Transaction)).all()
