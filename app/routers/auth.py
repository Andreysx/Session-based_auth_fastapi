from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import User
from app.schemas import UserCreate
from app.db_depends import get_async_db
from app.security import verify_password
from app.sessions import create_session, delete_session, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(path="/login", status_code=status.HTTP_200_OK)
async def login(user_data: UserCreate, response: Response, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(select(User).where(User.email == user_data.email))
    user = result.first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    await create_session(user.id, response)

    return {"message": "Login in"}


@router.post(path="/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response):
    await delete_session(request, response)
    return {"message": "Logged out"}


@router.get(path="/me", status_code=status.HTTP_200_OK)
async def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
