from fastapi import FastAPI

from app.src.presentation.routers.order_router import router as order_router

app = FastAPI(title="order-service")
app.include_router(order_router)
