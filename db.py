from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlmodel import Session, create_engine, SQLModel

DATABASE_NAME = "db.sqlite3"
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)


@asynccontextmanager
async def create_all_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
