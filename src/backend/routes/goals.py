from __future__ import annotations
from sqlmodel import Session, SQLModel
from src.backend.database import engine
from src.backend.database.orm import Goal
from pydantic import BaseModel


class GoalRequest(BaseModel):
    title: str
    description: str
    price: float | None


def goal_create(goal_data, user_id) -> Goal:
    goal = Goal(
        title=goal_data.title,
        description=goal_data.description,
        price=goal_data.price,
        user_id=user_id
    )


    with Session(engine) as transaction:
        Goal.create(goal, transaction)

    return goal







