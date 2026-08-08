from fastapi import APIRouter
from models import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=Transaction)
async def create_transaction(transaction_data: Transaction):
    return transaction_data
