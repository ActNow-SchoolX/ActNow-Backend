from __future__ import annotations
from fastapi import APIRouter
from sqlmodel import Session
from pydantic import BaseModel, validator

from src.backend.database import engine
from src.backend.database.orm import Goal


app = APIRouter()


class GoalRequest(BaseModel):
    goal_id: int
    title: str | None
    description: str | None
    price: float | None = None
    deadline: float | None = None

    @validator('all')
    def check_change(cls, title, description, price, deadline):
        if title & description & price & deadline is None:
            raise ValueError('No changes')
        return title, description, price, deadline


class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    price: float
    deadline: float  | None


def goal_update(goal_data, user_id) -> Goal:
    goal = Goal(
        title=goal_data.title,
        description=goal_data.description,
        price=goal_data.price,
        user_id=user_id,
        deadline=goal_data.deadline
    )

    with Session(engine) as transaction:
        goal = Goal.update(goal, transaction)

    return goal