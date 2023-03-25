from datetime import datetime

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
    # check if fields are not empty
    if item.title is None and item.description is None and item.price is None and item.deadline is None:
        raise HTTPException(status_code=400, detail="At least one field must be specified.")

    with Session(engine) as transaction:
        goal = Goal.get_by_id(transaction, goal_id)

        if goal is None:
            raise HTTPException(status_code=404, detail="Goal with specified id is not found.")

        if goal.deleted:
            raise HTTPException(status_code=404, detail="Goal with specified id is not found.")

        if goal.user_id != session.user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        if item.title is not None:
            goal.title = item.title
        if item.description is not None:
            goal.description = item.description
        if item.price is not None:
            goal.price = item.price
        if item.deadline is not None:
            goal.deadline = datetime.fromtimestamp(item.deadline)

        goal.update(transaction)

        if goal.deadline is not None:
            goal.deadline = goal.deadline.timestamp()

        return goal
