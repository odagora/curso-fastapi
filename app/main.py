from fastapi import FastAPI
from datetime import datetime
from zoneinfo import ZoneInfo
from models import (
    CustomerPublic,
)
from .routers import customers, transactions, invoices, plans
from db import create_all_tables

app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(invoices.router)
app.include_router(plans.router)

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
