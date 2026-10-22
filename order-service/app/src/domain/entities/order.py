"""Entidades de dominio: lo que el caso de uso conoce de una orden.

Son clases normales de Python. No importan SQLModel ni psycopg.
"""
import uuid
from enum import Enum

from app.src.shared.utils.date import utc_now


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class OrderItem:
    def __init__(self, product_id, quantity, unit_price, id=None):
        if id is None:
            id = uuid.uuid4()

        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price

    def subtotal(self):
        return self.unit_price * self.quantity


class Order:
    def __init__(
        self,
        user_id,
        items,
        status=OrderStatus.PENDING,
        total=0,
        id=None,
        created_at=None,
        updated_at=None,
    ):
        # Si no recibimos un id o unas fechas, es una orden nueva: los generamos.
        if id is None:
            id = uuid.uuid4()
        if created_at is None:
            created_at = utc_now()
        if updated_at is None:
            updated_at = created_at

        self.id = id
        self.user_id = user_id
        self.items = items
        self.status = status
        self.total = total
        self.created_at = created_at
        self.updated_at = updated_at
