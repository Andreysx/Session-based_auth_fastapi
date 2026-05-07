from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
