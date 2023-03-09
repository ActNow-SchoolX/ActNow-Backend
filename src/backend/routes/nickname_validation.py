from pydantic import BaseModel

from src.backend.app import app
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from src.backend.internals.nickname_validation import nickname_validation


class ModelRequest(BaseModel):
    nickname: str


@app.get('/validate_nickname')
def validate_nickname(request: ModelRequest):
    value = request.nickname

    if nickname_validation():
        ...

    r = {"nickname": value, "available": True}

    return JSONResponse(content=r, status_code=200)
