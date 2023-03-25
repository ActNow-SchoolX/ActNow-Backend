from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import User, Story
from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData

app = APIRouter()


@app.post('/story/like/{story_id}', dependencies=[Depends(cookie)], status_code=200)
async def like_story(
        story_id: int,
        session: SessionData = Depends(verifier)
):
    with Session(engine) as transaction:
        user = User.get_by_id(transaction, session.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        story = Story.get_by_id(transaction, story_id)

        if not story:
            raise HTTPException(status_code=404, detail="Story not found.")

        if story in user.liked_stories:
            raise HTTPException(status_code=409, detail="Story already liked.")

        user.like_story(transaction, story_id)

        return {"status": True}


@app.post('/story/dislike/{story_id}', dependencies=[Depends(cookie)], status_code=200)
async def dislike_story(
        story_id: int,
        session: SessionData = Depends(verifier)
):
    with Session(engine) as transaction:
        user = User.get_by_id(transaction, session.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        story = Story.get_by_id(transaction, story_id)

        if not story:
            raise HTTPException(status_code=404, detail="Story not found.")

        if story not in user.liked_stories:
            raise HTTPException(status_code=409, detail="Story already disliked.")

        user.dislike_story(transaction, story_id)

        return {"status": True}
