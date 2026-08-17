from enum import Enum
from typing import Annotated
from phonenumbers import (
    parse,
    is_valid_number,
    format_number,
    PhoneNumberFormat,
    NumberParseException,
)
from pydantic import BaseModel, Field, EmailStr, computed_field, field_validator
from sqlmodel import Relationship, SQLModel, Field


class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class CustomerPlan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="plan.id")
    customer_id: int = Field(foreign_key="customer.id")
    status: StatusEnum = Field(default=StatusEnum.ACTIVE)


class PlanBase(SQLModel):
    name: str
    price: int
    description: str


class Plan(PlanBase, table=True):
    """The real table in the database."""

    id: int | None = Field(default=None, primary_key=True)
    customers: list["Customer"] = Relationship(
        back_populates="plans", link_model=CustomerPlan
    )


class PlanCreate(PlanBase):
    """What the client sends to create a new plan."""


class PlanPublic(PlanBase):
    """What the server returns to client"""

    id: int


class CustomerBase(SQLModel):
    name: str
    description: str | None = None
    email: EmailStr
    age: Annotated[int, Field(gt=0, lt=120)]
    phone: str | None = None
    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if not value:
            return value
        try:
            parsed = parse(value)
            if not is_valid_number(parsed):
                raise ValueError("invalid phone number")
        except NumberParseException as e:
            if "default region" in str(e).lower():
                raise ValueError(
                    "phone number must include country code (e.g., +57...)"
                )
            raise ValueError("invalid phone format")
        return format_number(parsed, PhoneNumberFormat.E164)


class Customer(CustomerBase, table=True):
    """The real table in the database."""

    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    transactions: list["Transaction"] = Relationship(back_populates="customer")
    plans: list[Plan] = Relationship(
        back_populates="customers", link_model=CustomerPlan
    )


class CustomerCreate(CustomerBase):
    """What the client sends to create a new customer."""


class CustomerPublic(CustomerBase):
    """What the server returns to client"""

    id: int


class CustomerUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    email: EmailStr | None = None
    age: Annotated[int | None, Field(gt=0, lt=120)] = None
    phone: str | None = None
    is_active: bool | None = None


class TransactionBase(SQLModel):
    amount: int
    description: str


class TransactionCreate(TransactionBase):
    customer_id: int = Field(foreign_key="customer.id")


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    customer: Customer = Relationship(back_populates="transactions")


class InvoiceRequest(BaseModel):
    id: int
    customer: CustomerPublic
    transactions: list[Transaction]


class InvoiceResponse(BaseModel):
    id: int
    customer: CustomerPublic
    transactions: list[Transaction]

    @computed_field
    @property
    def total_amount(self) -> int:
        return sum(transaction.amount for transaction in self.transactions)
