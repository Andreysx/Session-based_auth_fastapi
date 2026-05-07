import uuid
from fastapi import Response, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.redis_client import redis_client
from app.models import User
from app.db_depends import get_async_db

# from passlib.context import CryptContext

SESSION_EXPIRE_SECONDS = 20


def create_session(user_id: str, response: Response):
    session_id = str(uuid.uuid4())

    redis_client.setex(
        f"session:{session_id}",
        SESSION_EXPIRE_SECONDS,
        user_id
    )

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax"
    )


async def get_current_user(request: Request, db: AsyncSession = Depends(get_async_db)):
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = redis_client.get(f"session:{session_id}")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    result = await db.scalars(select(User).where(User.id == int(user_id)))
    user = result.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def delete_session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")

    if session_id:
        redis_client.delete(f"session:{session_id}")

    response.delete_cookie("session_id")
