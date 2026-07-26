from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlmodel import select
from models import (
    Customer,
    CustomerPublic,
    CustomerCreate,
    CustomerUpdate,
    Transaction,
    InvoiceRequest,
    InvoiceResponse,
)
from db import SessionDep, create_all_tables

app = FastAPI(lifespan=create_all_tables)

TIME_ZONES = {
    "CO": "America/Bogota",
    "US": "America/New_York",
    "MX": "America/Mexico_City",
    "BR": "America/Sao_Paulo",
}

db_customers: dict[int, CustomerPublic] = {}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/time")
async def get_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": current_time}


@app.get("/time/{country_code}")
async def get_time_by_country_with_format(country_code: str, format: str = "iso"):
    country_code = country_code.upper()
    time_zone = TIME_ZONES.get(country_code, "UTC")
    current_time = datetime.now(ZoneInfo(time_zone))

    if format == "24h":
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    elif format == "12h":
        formatted_time = current_time.strftime("%Y-%m-%d %I:%M:%S %p")
    else:
        formatted_time = current_time.isoformat()

    return {
        "current_time": formatted_time,
        "country_code": country_code,
        "format": format,
    }


@app.post("/customers", response_model=CustomerPublic)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@app.get("/customers", response_model=list[CustomerPublic])
async def list_customers(session: SessionDep):
    return session.exec(select(Customer)).all()


@app.get("/customers/{id}", response_model=CustomerPublic)
async def get_customer(id: int, session: SessionDep):
    customer = session.get(Customer, id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    return customer


@app.patch("/customers/{id}", response_model=CustomerPublic)
async def update_customer(id: int, customer_data: CustomerUpdate, session: SessionDep):
    customer = session.get(Customer, id)
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


@app.delete("/customers/{id}")
async def delete_customer(id: int, session: SessionDep):
    customer = session.get(Customer, id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    session.delete(customer)
    session.commit()
    return {"detail": "ok"}


@app.post("/transactions")
async def create_transaction(transaction_data: Transaction):
    return transaction_data


@app.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(invoice: InvoiceRequest):
    return InvoiceResponse(
        id=invoice.id,
        customer=invoice.customer,
        transactions=invoice.transactions,
    )
