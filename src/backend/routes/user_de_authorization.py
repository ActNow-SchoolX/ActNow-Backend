from fastapi import FastAPI, Depends, Response, APIRouter
from src.backend.dependencies import cookie, backend
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/logout", response_model=None)
async def logout(response: Response, session_uuid=Depends(cookie)):
    await backend.delete(session_uuid)
    cookie.delete_from_response(response)
    return JSONResponse(content={"message": "Logged out successfully"})
