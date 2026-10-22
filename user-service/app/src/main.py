from fastapi import FastAPI

from app.src.presentation.routers.user_router import router as user_router

app = FastAPI(title="user-service")
app.include_router(user_router)
