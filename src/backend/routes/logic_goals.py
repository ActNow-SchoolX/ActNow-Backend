from fastapi import APIRouter, Depends, HTTPException
from typing import List

from src.backend.database import engine
from src.backend.dependencies import cookie, verifier
from src.backend.internals.goals import Goal, GoalRequest, GoalResponse, goal_create
from src.backend.sessions import SessionData
from src.backend.database.orm import User
from src.backend.database.orm import Story, Session

app = APIRouter()


@app.delete('/goal/{goal_id}', response_model=GoalResponse, dependencies=[Depends(cookie)], status_code=200)
async def delete_goal(goal_id: int, session: SessionData = Depends(verifier)):
    with Session(engine) as transaction:
        goal = Goal.get_by_id(transaction, goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found.")
        if goal.deleted:
            raise HTTPException(status_code=404, detail="Goal not found.")

        # реализовать проверку на авторство!

        goal.delete(transaction)
        return goal


# @app.delete('/goal', response_model=List[GoalResponse], dependencies=[Depends(cookie)], status_code=200)
async def delete_goal_by_request(delete_request: List[int], session: SessionData = Depends(verifier)):
    with Session(engine) as transaction:
        goals = []
        for goal_id in delete_request:
            goal = Goal.get_by_id(transaction, goal_id)
            if not goal:
                continue
            if goal.deleted:
                continue
            goal.delete(transaction)
            goals.append(GoalResponse.from_orm(goal))
        return goals
