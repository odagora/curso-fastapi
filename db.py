from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine

DATABASE_NAME = "db.sqlite3"
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
