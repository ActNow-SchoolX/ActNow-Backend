from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile
from story_create import story_create, StoryResponse, StoryRequest
from src.backend.sessions import SessionData
from src.backend.dependencies import cookie, backend, verifier

app = APIRouter()


def create_file(file: UploadFile):
    file_path = rf'{file.filename}'
    return file_path


@app.post('/story', response_model=StoryResponse, dependencies=[Depends(cookie)])
async def create_goal(response: Response, item: StoryRequest, session: SessionData = Depends(verifier)):


    story = story_create(item, session.user_id)
    return StoryResponse(user_id=story.user_id,
                         story_id=story.id,
                         photo=create_file(),
                         description=story.description,
                         )

