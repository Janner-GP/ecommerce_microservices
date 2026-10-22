import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.src.shared.utils.date import utc_now

# Se importa para que SQLModel conozca la tabla a la que apunta category_id.
from app.src.domain.models.category import Category  # noqa: F401


# Modelo de persistencia (tabla). Lo usan Alembic y SQLModelProductRepository.
# La entidad que maneja el caso de uso está en domain/entities/product.py.
class Product(SQLModel, table=True):
    __tablename__ = "cat_products"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    category_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="cat_categories.id",
        index=True,
    )
    sku: str = Field(unique=True, max_length=50)
    name: str = Field(index=True, max_length=150)
    description: str | None = None
    price: Decimal = Field(max_digits=12, decimal_places=2)
    stock: int = Field(default=0)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
