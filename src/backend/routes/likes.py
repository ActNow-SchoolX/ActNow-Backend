from fastapi import APIRouter, Depends, HTTPException

from src.backend.database.orm import User
from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData

app = APIRouter()

@app.post('/like-story/{story_id}', dependencies=[Depends(cookie)], status_code=200)
async def like_story(
        story_id: int,
        session: SessionData = Depends(verifier)
):
    user = User.get_by_id(session, session.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    story = Story.get_by_id(session, story_id)

    if not story:
        raise HTTPException(status_code=404, detail="Story not found.")

    if story in user.liked_stories:
        user.liked_stories.remove(story)
    else:
        user.liked_stories.append(story)

    session.add(user)
    session.commit()
    session.refresh(user)

    return {"status": "success", "liked_stories": [s.id for s in user.liked_stories]}
