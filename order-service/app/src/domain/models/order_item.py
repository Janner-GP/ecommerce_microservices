import uuid
from decimal import Decimal

from sqlmodel import Field, SQLModel


class OrderItem(SQLModel, table=True):
    __tablename__ = "ord_order_items"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # La orden está en este mismo servicio, así que sí lleva foreign key.
    order_id: uuid.UUID = Field(foreign_key="ord_orders.id", index=True)

    # El producto vive en catalog-service: solo guardamos su id.
    product_id: uuid.UUID = Field(index=True)

    quantity: int
    unit_price: Decimal = Field(max_digits=12, decimal_places=2)
