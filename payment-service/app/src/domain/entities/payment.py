"""Entidad de dominio: lo que el caso de uso conoce de un pago.

Es una clase normal de Python. No importa SQLModel ni psycopg.
"""
import uuid
from enum import Enum

from app.src.shared.utils.date import utc_now


class PaymentMethod(str, Enum):
    CARD = "CARD"
    PSE = "PSE"
    CASH = "CASH"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Payment:
    def __init__(
        self,
        order_id,
        amount,
        method,
        status=PaymentStatus.PENDING,
        id=None,
        created_at=None,
        updated_at=None,
    ):
        # Si no recibimos un id o unas fechas, es un pago nuevo: los generamos.
        if id is None:
            id = uuid.uuid4()
        if created_at is None:
            created_at = utc_now()
        if updated_at is None:
            updated_at = created_at

        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.method = method
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
