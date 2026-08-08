from fastapi import HTTPException, status, APIRouter
from sqlmodel import select
from models import CustomerPublic, CustomerCreate, Customer, CustomerUpdate
from db import SessionDep

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerPublic)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.get("", response_model=list[CustomerPublic])
async def list_customers(session: SessionDep):
    return session.exec(select(Customer)).all()


@router.get("/{id}", response_model=CustomerPublic)
async def get_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    return customer


@router.patch("/{id}", response_model=CustomerPublic)
async def update_customer(
    customer_id: int, customer_data: CustomerUpdate, session: SessionDep
):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    update_data = customer_data.model_dump(exclude_unset=True)
    customer.sqlmodel_update(update_data)

    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.delete("/{id}")
async def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    session.delete(customer)
    session.commit()
    return {"detail": "ok"}
