from fastapi import FastAPI

from app.src.presentation.routers.product_router import router as product_router

app = FastAPI(title="catalog-service")
app.include_router(product_router)
