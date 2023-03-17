from fastapi import APIRouter, Depends

from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData
from src.backend.database.orm import Goal

from sqlmodel import Session
from src.backend.database import engine

app = APIRouter()

@app.get("/get_goals")
def get_goals_by_userid():
    pass


@app.get("/get_goal", dependencies=[Depends(cookie)])
def get_goal_by_id(goal_id: int, session: SessionData = Depends(verifier)) -> Goal:

    with Session(engine) as transaction:
        goal = Goal.get_by_id(transaction, goal_id)

    return goal
