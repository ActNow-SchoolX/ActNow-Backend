from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, validator, Field
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import Goal


class GoalRequest(BaseModel):
    title: str
    description: str
    price: float | None = None
    deadline: float | None = None

    @validator('title')
    def check_title(cls, title):
        if len(title) > 79:
            raise ValueError('Название голса превышает возможное количество символов')
        return title

    @validator('description')
    def check_description(cls, description):
        if len(description) > 1000:
            raise ValueError('Описание голса превышает возможное количество символов')
        return description

    @validator('deadline', )
    def check_deadline(cls, deadline):
        now = datetime.now().timestamp()
        diff = deadline - now
        if diff < 3600:
            raise ValueError('Недопустимое время')
        return deadline

    @validator('price')
    def check_price(cls, price):
        if price is not None:
            if price < 1:
                raise ValueError('Стоимость должна превышать 1 рубль')
            return price


class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    price: float
    deadline: float | None


def goal_create(goal_data, user_id) -> Goal:
    goal = Goal(
        title=goal_data.title,
        description=goal_data.description,
        price=goal_data.price,
        user_id=user_id,
        deadline=goal_data.deadline
    )

    with Session(engine) as transaction:
        goal = Goal.create(goal, transaction)

        goal.deadline = goal.deadline.timestamp()

    return goal
