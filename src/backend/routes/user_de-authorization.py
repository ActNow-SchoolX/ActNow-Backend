from fastapi import FastAPI, Depends
from fastapi.openapi.models import Response

from src.backend.dependencies import backend, cookie

app = FastAPI()


@app.post("/logout")
async def logout(response: Response, session_uuid: Depends(cookie)):
    await backend.delete(session_uuid)
    cookie.delete_from_response(response)
    return {"message": "Logged out successfully"}
