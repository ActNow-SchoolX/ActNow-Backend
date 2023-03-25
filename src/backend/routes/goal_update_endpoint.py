from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import Goal
from src.backend.dependencies import verifier, cookie
from src.backend.internals.goals import GoalPatchRequest, GoalResponse
from src.backend.sessions import SessionData

app = APIRouter()


@app.patch("/goal/{goal_id}", response_model=GoalResponse, dependencies=[Depends(cookie)], status_code=200)
async def update_goal(goal_id: int, item: GoalPatchRequest, session: SessionData = Depends(verifier)):
    with Session(engine) as transaction:
        goal = Goal.get_by_id(transaction, goal_id)

        if goal is None:
            raise HTTPException(status_code=404, detail="Goal with specified id is not found.")

        if goal.deleted:
            raise HTTPException(status_code=404, detail="Goal with specified id is not found.")

        if goal.user_id != session.user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        goal.title = item.title
        goal.description = item.description
        goal.price = item.price
        goal.deadline = item.deadline

        goal.update(transaction)

        return goal
