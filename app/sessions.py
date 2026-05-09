import secrets
import hashlib
from fastapi import Response, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.redis_client import async_redis_client
from app.models import User
from app.db_depends import get_async_db

# from passlib.context import CryptContext

SESSION_EXPIRE_SECONDS = 15


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_session(user_id: str, response: Response):
    session_token = secrets.token_urlsafe(32)

    session_hash = hash_session_token(session_token)

    await async_redis_client.setex(
        f"session:{session_hash}",
        SESSION_EXPIRE_SECONDS,
        user_id
    )

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # local
        samesite="lax",
        max_age=SESSION_EXPIRE_SECONDS
    )


async def get_current_user(request: Request, db: AsyncSession = Depends(get_async_db)):
    session_token = request.cookies.get("session_token")

    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session_hash = hash_session_token(session_token)

    user_id = await async_redis_client.get(f"session:{session_hash}")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    # # обновление TTL(time to live) сессии при активности
    # await async_redis_client.expire(
    #     f"session:{session_hash}",
    #     SESSION_EXPIRE_SECONDS
    # )
    # Добавить reset cookie
    result = await db.scalars(select(User).where(User.id == int(user_id)))
    user = result.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


async def delete_session(request: Request, response: Response):
    session_token = request.cookies.get("session_token")

    if session_token:
        session_hash = hash_session_token(session_token)

        await async_redis_client.delete(f"session:{session_hash}")

    response.delete_cookie(key="session_token",
                           httponly=True,
                           secure=False,  # local
                           samesite="lax")
