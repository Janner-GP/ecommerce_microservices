import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.src.domain.entities.payment import PaymentMethod, PaymentStatus
from app.src.shared.utils.date import utc_now


# Modelo de persistencia (tabla). Lo usan Alembic y SQLModelPaymentRepository.
# La entidad que maneja el caso de uso está en domain/entities/payment.py.
class Payment(SQLModel, table=True):
    __tablename__ = "pym_payments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # La orden vive en order-service: aquí solo guardamos su id (sin foreign key).
    order_id: uuid.UUID = Field(unique=True, index=True)

    amount: Decimal = Field(max_digits=12, decimal_places=2)
    method: PaymentMethod
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
