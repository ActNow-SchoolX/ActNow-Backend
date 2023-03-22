from fastapi import APIRouter, Depends

from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData
from src.backend.database.orm import Goal

from sqlmodel import Session
from src.backend.database import engine

app = APIRouter()


@app.get("/get_goal/{goal.id}", dependencies=[Depends(cookie)])
def get_goal_by_id(goal_id: int) -> Goal:

    with Session(engine) as transaction:
        goal = Goal.get_by_id(transaction, goal_id)

    return goal
