from fastapi import FastAPI

from app.src.presentation.routers.notification_router import router as notification_router

app = FastAPI(title="notification-service")
app.include_router(notification_router)
