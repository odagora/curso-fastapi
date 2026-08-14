from fastapi import HTTPException, status, APIRouter
from sqlmodel import and_, select
from models import (
    CustomerPlan,
    CustomerPublic,
    CustomerCreate,
    Customer,
    CustomerUpdate,
    Plan,
)
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


@router.post(
    "/{customer_id}/plans/{plan_id}",
    response_model=CustomerPlan,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe_customer_to_plan(
    customer_id: int, plan_id: int, session: SessionDep
):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)
    if not customer_db or not plan_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer or Plan not found"
        )
    customer_plan = CustomerPlan(plan_id=plan_id, customer_id=customer_id)
    session.add(customer_plan)
    session.commit()
    session.refresh(customer_plan)
    return customer_plan


@router.get("/{customer_id}/plans", response_model=list[Plan])
async def list_customer_active_plans(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    active_plans_db = session.exec(
        select(Plan)
        .join(CustomerPlan)
        .where(
            and_(
                CustomerPlan.customer_id == customer_id, CustomerPlan.is_active == True
            )
        )
    ).all()
    return active_plans_db
