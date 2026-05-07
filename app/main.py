from fastapi import FastAPI
from app.routers import users, auth, test

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(test.router)


@app.get(path="/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Демонстрация session-based authentification"}
