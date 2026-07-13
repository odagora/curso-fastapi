from fastapi import FastAPI
from datetime import datetime
from zoneinfo import ZoneInfo
from models import Customer, Transaction, InvoiceRequest, InvoiceResponse

app = FastAPI()

TIME_ZONES = {
    "CO": "America/Bogota",
    "US": "America/New_York",
    "MX": "America/Mexico_City",
    "BR": "America/Sao_Paulo",
}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/time")
async def get_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": current_time}


@app.get("/time/{country_code}")
async def get_time_by_country(country_code: str):
    country_code = country_code.upper()
    if country_code not in TIME_ZONES:
        return {"error": "Invalid country code"}

    time_zone = TIME_ZONES[country_code]
    current_time = datetime.now(ZoneInfo(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": current_time, "country_code": country_code}


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


@app.post("/customers")
async def create_customer(customer_data: Customer):
    return customer_data


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
