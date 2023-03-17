from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile, File

from src.backend.dependencies import cookie, verifier
from src.backend.routes.story_create import story_create, StoryResponse
from src.backend.sessions import SessionData

app = APIRouter()


# Уточните, нужен ли он вам
def create_file(file: UploadFile):
    file_path = rf'{file.filename}'
    return file_path


@app.post('/story', response_model=StoryResponse, dependencies=[Depends(cookie)], status_code=201)
async def create_goal(
        goal_id: int,
        description: str,
        photo: UploadFile = File(...),
        session: SessionData = Depends(verifier)
):
    filename = f'{str(uuid4())}.{photo.filename.split(".")[-1]}'

    upload_dir = Path(__file__).parent.parent.parent.parent / "uploads"
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / filename

    with file_path.open("wb+") as file_object:
        file_object.write(photo.file.read())

    # реализуйте валидацию голса, который точно должен быть в базе
    ...

    # реализуйте валидацию описания по таске (у вас уже есть валидатор, попробуйте пришить его сюда)
    ...

    story = story_create(session.user_id, goal_id, description, str(file_path))

    return story

