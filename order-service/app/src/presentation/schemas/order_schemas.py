"""Contrato HTTP: no cambia aunque cambie el adaptador de persistencia."""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.src.domain.entities.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class OrderCreate(BaseModel):
    user_id: uuid.UUID
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal


class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: OrderStatus
    total: Decimal
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
