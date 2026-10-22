"""La misma prueba se ejecuta con los dos adaptadores: deben cumplir el mismo contrato.

Requiere una base con las migraciones aplicadas:
    TEST_DATABASE_URL=postgresql://... uv run pytest
Al final se hace rollback, así que no deja datos.
"""
import os
import uuid
from decimal import Decimal

import psycopg
import pytest
from sqlmodel import Session, create_engine

from app.src.application.use_cases.create_order import CreateOrder
from app.src.domain.entities.order import Order, OrderItem, OrderStatus
from app.src.infrastructure.repositories.postgres_order_repository import (
    PostgresOrderRepository,
)
from app.src.infrastructure.repositories.sqlmodel_order_repository import (
    SQLModelOrderRepository,
)

DB_URL = os.getenv("TEST_DATABASE_URL")
skip_without_db = pytest.mark.skipif(DB_URL is None, reason="TEST_DATABASE_URL no definida")


def check_repository(repository):
    order = Order(
        user_id=uuid.uuid4(),
        items=[
            OrderItem(product_id=uuid.uuid4(), quantity=2, unit_price=Decimal("45000.00")),
            OrderItem(product_id=uuid.uuid4(), quantity=1, unit_price=Decimal("10000.00")),
        ],
    )

    created = CreateOrder(repository).execute(order)

    assert isinstance(created, Order)
    assert created.total == Decimal("100000.00")
    assert created.status == OrderStatus.PENDING
    assert len(created.items) == 2

    found = repository.get_by_id(order.id)
    assert found.total == Decimal("100000.00")
    assert len(found.items) == 2


@skip_without_db
def test_sqlmodel_repository():
    engine = create_engine(DB_URL.replace("postgresql://", "postgresql+psycopg://"))
    session = Session(engine)

    check_repository(SQLModelOrderRepository(session))

    session.rollback()
    session.close()


@skip_without_db
def test_postgres_repository():
    connection = psycopg.connect(DB_URL)

    check_repository(PostgresOrderRepository(connection))

    connection.rollback()
    connection.close()
