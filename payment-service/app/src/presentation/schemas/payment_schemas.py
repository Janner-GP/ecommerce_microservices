"""Contrato HTTP: no cambia aunque cambie el adaptador de persistencia."""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.src.domain.entities.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    order_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    method: PaymentMethod


class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
