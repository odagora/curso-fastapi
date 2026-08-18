from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlmodel import func, select
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


@router.get(
    "",
    response_model=list[Transaction],
    responses={
        200: {
            "headers": {
                "X-Total-Count": {"description": "Total number of transactions", "schema": {"type": "integer"}},
                "X-Page-Count": {"description": "Items in current page", "schema": {"type": "integer"}},
            }
        }
    },
)
async def list_transactions(
    session: SessionDep,
    response: Response,
    cursor: int | None = Query(None, description="Last transaction ID seen"),
    limit: int = Query(10, description="Number of items to return", le=100),
):
    query = select(Transaction)
    if cursor is not None:
        query = query.where(Transaction.id > cursor)  # type: ignore[operator]
    query = query.order_by(Transaction.id).limit(limit)  # type: ignore[operator]
    transactions = list(session.exec(query).all())

    total: int = session.exec(
        select(func.count(Transaction.id))  # type: ignore[arg-type]
    ).one()

    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page-Count"] = str(len(transactions))

    return transactions
