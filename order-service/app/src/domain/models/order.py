import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.src.domain.entities.order import OrderStatus
from app.src.shared.utils.date import utc_now


# Modelo de persistencia (tabla). Lo usan Alembic y SQLModelOrderRepository.
# La entidad que maneja el caso de uso está en domain/entities/order.py.
class Order(SQLModel, table=True):
    __tablename__ = "ord_orders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # El usuario vive en user-service: aquí solo guardamos su id (sin foreign key).
    user_id: uuid.UUID = Field(index=True)

    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total: Decimal = Field(max_digits=12, decimal_places=2)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
