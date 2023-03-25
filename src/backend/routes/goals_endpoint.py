from fastapi import APIRouter, Depends, HTTPException

from src.backend.dependencies import cookie, verifier
from src.backend.internals.goals import GoalRequest, GoalResponse, goal_create
from src.backend.sessions import SessionData
from src.backend.database.orm import Goal

from sqlmodel import Session
from src.backend.database import engine

app = APIRouter()


@app.post('/goal', response_model=GoalResponse, dependencies=[Depends(cookie)], status_code=201)
async def create_goal(item: GoalRequest, session: SessionData = Depends(verifier)):

    new_goal = goal_create(item, session.user_id)

    return new_goal


@app.get("/goal/{goal_id}", dependencies=[Depends(cookie)])
def get_goal_by_id(goal_id: int) -> Goal:

    with Session(engine) as transaction:
        goal = Goal.get_by_id(transaction, goal_id)

        if goal is None or goal.deleted is True:
            raise HTTPException(status_code=404, detail="Goal with specified id is not found.")

        return goal
