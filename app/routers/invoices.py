from fastapi import APIRouter
from models import InvoiceRequest, InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceResponse)
async def create_invoice(invoice: InvoiceRequest):
    return InvoiceResponse(
        id=invoice.id,
        customer=invoice.customer,
        transactions=invoice.transactions,
    )
