from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from src.backend.database import get_session
from src.backend.sessions import FastAPISession
from src.backend.internals import add_like, remove_like, get_like_status

router = APIRouter()


# эндпойнт для добавления лайка
@router.post("/likes/{item_id}")
async def like_item(
        item_id: int,
        session: FastAPISession = Depends(),
        db: Session = Depends(get_session),
):
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")

    # проверяем, не поставил ли пользователь уже лайк или отменил его
    like_status = get_like_status(db, item_id, user_id)
    if like_status == "liked":
        raise HTTPException(status_code=400, detail="User has already liked the item")
    elif like_status == "unliked":
        raise HTTPException(status_code=400, detail="User has already unliked the item")

    try:
        add_like(db, item_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": f"Item {item_id} was liked"}


@router.delete("/likes/{item_id}")
async def unlike_item(
        item_id: int,
        session: FastAPISession = Depends(),
        db: Session = Depends(get_session),
):
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")

    # проверяем, не отменил ли пользователь уже лайк
    like_status = get_like_status(db, item_id, user_id)
    if like_status == "unliked":
        raise HTTPException(status_code=400, detail="User has already unliked the item")
    elif like_status == "not_liked":
        raise HTTPException(status_code=400, detail="User has not liked the item yet")

    try:
        remove_like(db, item_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": f"Like for item {item_id} was removed"}
