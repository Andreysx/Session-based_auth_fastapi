from fastapi import APIRouter, Depends, HTTPException, status
from app.models.users import User
from app.auth import get_current_user

router = APIRouter(prefix="/test", tags=["test"])


@router.get(path="/protected", status_code=status.HTTP_200_OK)
async def protected_route(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.email}"}
