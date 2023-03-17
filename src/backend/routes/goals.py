from __future__ import annotations
from sqlmodel import Session, SQLModel
from src.backend.database import engine
from src.backend.database.orm import Goal
from pydantic import BaseModel, validator
from datetime import datetime
import dateutil.parser


class GoalRequest(BaseModel):
    user_id: str
    title: str
    description: str
    price: float | None
    deadline: datetime | None

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

    @validator('deadline')
    def check_deadline(cls, deadline):
        now = datetime.datetime.now()
        diff = deadline - now
        if diff.total_seconds() < 3600:
            raise ValueError('Недопустимое время')
        return deadline

    @validator('price')
    def check_price(cls, price):
        if price is not None:
            if price < 1:
                raise ValueError('Прайс должен превышать 1 рубль')
            return price


class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    price: float
    deadline: datetime


def goal_create(goal_data, user_id) -> Goal:
    goal = Goal(
        title=goal_data.title,
        description=goal_data.description,
        price=goal_data.price,
        user_id=user_id,
        deadline=goal_data.deadline
    )

    with Session(engine) as transaction:
        Goal.create(goal, transaction)

    goal.id = goal.id

    return goal
