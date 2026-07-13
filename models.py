from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, computed_field


class Customer(BaseModel):
    name: str
    description: str | None = None
    email: EmailStr
    age: Annotated[int, Field(gt=0, lt=120)]
    phone: str | None = None
    is_active: bool = True


class Transaction(BaseModel):
    id: int
    amount: int
    description: str


class InvoiceRequest(BaseModel):
    id: int
    customer: Customer
    transactions: list[Transaction]


class InvoiceResponse(BaseModel):
    id: int
    customer: Customer
    transactions: list[Transaction]

    @computed_field
    @property
    def total_amount(self) -> int:
        return sum(transaction.amount for transaction in self.transactions)
