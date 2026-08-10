from fastapi import APIRouter, status
from sqlmodel import select

from db import SessionDep
from models import Plan, PlanCreate, PlanPublic

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", response_model=PlanPublic, status_code=status.HTTP_201_CREATED)
async def create_plan(plan_data: PlanCreate, session: SessionDep):
    plan = Plan.model_validate(plan_data)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


@router.get("", response_model=list[PlanPublic])
async def list_plans(session: SessionDep):
    return session.exec(select(Plan)).all()
