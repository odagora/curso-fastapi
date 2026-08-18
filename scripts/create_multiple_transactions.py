from sqlmodel import Session
from db import engine
from models import Customer, Transaction

with Session(engine) as session:
    customer = Customer(name="Test", email="test@example.com", age=30)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    assert customer.id is not None
    for i in range(50):
        tx = Transaction(
            amount=i * 100, description=f"Transaction {i}", customer_id=customer.id
        )
        session.add(tx)
    session.commit()
