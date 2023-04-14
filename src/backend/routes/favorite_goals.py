from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import User, Goal
from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData

app = APIRouter()


@app.post('/goal/favorite/{goal_id}', dependencies=[Depends(cookie)], status_code=200)
async def goal_favorite(
        goal_id: int,
        session: SessionData = Depends(verifier)
):
    with Session(engine) as transaction:
        user = User.get_by_id(transaction, session.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        goal = Goal.get_by_id(transaction, goal_id)

        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found.")

        if goal in user.goal_favorites:
            raise HTTPException(status_code=409, detail="Goal already in favorites.")

        user.add_favorite_goal(transaction, goal_id)

        return {"status": True}


@app.post('/goal/remove/{goal_id}', dependencies=[Depends(cookie)], status_code=200)
async def remove_goal(
        goal_id: int,
        session: SessionData = Depends(verifier)
):
    with Session(engine) as transaction:
        user = User.get_by_id(transaction, session.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        goal = Goal.get_by_id(transaction, goal_id)

        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found.")

        if goal not in user.goal_favorites:
            raise HTTPException(status_code=409, detail="Goal is not in favorites.")

        user.not_favorite_goal(transaction, goal_id)

        return {"status": True}