from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.backend.dependencies import cookie, verifier
from src.backend.internals.stories import story_create, StoryResponse, check_photo, validate_goal_exists, \
    check_description
from src.backend.sessions import SessionData

app = APIRouter()


@app.post('/story', response_model=StoryResponse, dependencies=[Depends(cookie)], status_code=201)
async def create_goal(
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


@app.get("./story/{story_id},", response_model=StoryResponse, dependencies=[Depends(cookie)])
async def get_story(story):
    if story is None or story.deleted is True:
        raise HTTPException(
            status_code=404
        )
    else:
        return story
