import secrets
import hashlib
from fastapi import Response, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.redis_client import async_redis_client
from app.models import User
from app.db_depends import get_async_db

SESSION_EXPIRE_SECONDS = 120


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
        secure=False,  # True in production (HTTPS only)
        samesite="lax",
        max_age=SESSION_EXPIRE_SECONDS,
        path="/"
    )


async def refresh_session(session_token: str, response: Response):
    session_hash = hash_session_token(session_token)

    ttl = await async_redis_client.ttl(
        f"session:{session_hash}"
    )

    if 0 < ttl < 30:
        # на этом этапе можно реализовать ротацию токена
        # в данном случае просто продление ttl
        await async_redis_client.expire(
            f"session:{session_hash}",
            SESSION_EXPIRE_SECONDS
        )

        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=False,  # True in production (HTTPS only)
            samesite="lax",
            max_age=SESSION_EXPIRE_SECONDS,
            path="/"
        )


async def delete_session(request: Request, response: Response):
    session_token = request.cookies.get("session_token")

    if session_token:
        session_hash = hash_session_token(session_token)

        await async_redis_client.delete(f"session:{session_hash}")

    response.delete_cookie(key="session_token",
                           httponly=True,
                           secure=False,  # True in production (HTTPS only)
                           samesite="lax",
                           path="/")


async def get_current_user(request: Request, response: Response, db: AsyncSession = Depends(get_async_db)):
    session_token = request.cookies.get("session_token")

    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session_hash = hash_session_token(session_token)

    user_id = await async_redis_client.get(f"session:{session_hash}")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    # # обновление TTL(time to live) сессии при активности в redis и cookies
    await refresh_session(session_token, response)

    result = await db.scalars(select(User).where(User.id == int(user_id)))
    user = result.first()

    if not user:
        await delete_session(request, response)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Мгновенная инвалидация(отзыв) сессии если данные пользователя изменены(пользователь заблокирован, is_active=False)
    # Можно создавать дополнительные слои авторизации и проверки прав пользователя
    if not user.is_active:
        await delete_session(request, response)

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    return user
