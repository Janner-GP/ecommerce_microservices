"""Contrato HTTP: no cambia aunque cambie el adaptador de persistencia."""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str = Field(max_length=50)
    name: str = Field(max_length=150)
    description: str | None = None
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    category_id: uuid.UUID | None = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID | None
    sku: str
    name: str
    description: str | None
    price: Decimal
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
