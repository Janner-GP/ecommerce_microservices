from fastapi import FastAPI

from app.src.presentation.routers.payment_router import router as payment_router

app = FastAPI(title="payment-service")
app.include_router(payment_router)
