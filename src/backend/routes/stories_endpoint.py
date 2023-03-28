from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import Story
from src.backend.dependencies import cookie, verifier
from src.backend.internals.stories import (
    story_create,
    StoryResponse,
    check_photo,
    validate_goal_exists,
    check_description,
)
from src.backend.sessions import SessionData

app = APIRouter()


@app.post('/story', response_model=StoryResponse, dependencies=[Depends(cookie)], status_code=201)
async def create_story(
        goal_id: int,
        description: str,
        photo: UploadFile = File(...),
        session: SessionData = Depends(verifier)
):
    try:
        photo = check_photo(photo)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    filename = f'{str(uuid4())}.{photo.filename.split(".")[-1]}'

    upload_dir = Path(__file__).parent.parent.parent.parent / "uploads"
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / filename

    with file_path.open("wb+") as file_object:
        file_object.write(photo.file.read())

    if not validate_goal_exists(goal_id):
        raise HTTPException(status_code=404, detail="Goal with specified id is not found.")

    try:
        description = check_description(description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    story = story_create(session.user_id, goal_id, description, str(file_path))

    return story


@app.get("/story/{story_id}", response_model=StoryResponse, dependencies=[Depends(cookie)], status_code=200)
async def get_story(story_id, session: SessionData = Depends(verifier)):
    with Session(engine) as transaction:
        story = Story.get_by_id(transaction, story_id)

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    if story.deleted:
        raise HTTPException(status_code=404, detail="Story not found")

    return story


@app.delete("/story/{story_id}", response_model=StoryResponse, dependencies=[Depends(cookie)], status_code=200)
async def story_delete(story_id: int, session: SessionData = Depends(verifier)):
    with Session(engine) as transaction:
        story = Story.get_by_id(transaction, story_id)

        if not story:
            raise HTTPException(status_code=404, detail="Story not found")

        if story.deleted:
            raise HTTPException(status_code=404, detail="Story not found")

        if story.user_id != session.user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        story.delete(transaction)

        return story
