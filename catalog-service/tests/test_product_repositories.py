"""La misma prueba se ejecuta con los dos adaptadores: deben cumplir el mismo contrato.

Requiere una base con las migraciones aplicadas:
    TEST_DATABASE_URL=postgresql://... uv run pytest
Al final se hace rollback, así que no deja datos.
"""
import os
from decimal import Decimal

import psycopg
import pytest
from sqlmodel import Session, create_engine

from app.src.application.use_cases.create_product import CreateProduct
from app.src.domain.entities.product import Product
from app.src.domain.exceptions import ProductAlreadyExistsError
from app.src.infrastructure.repositories.postgres_product_repository import (
    PostgresProductRepository,
)
from app.src.infrastructure.repositories.sqlmodel_product_repository import (
    SQLModelProductRepository,
)

DB_URL = os.getenv("TEST_DATABASE_URL")
skip_without_db = pytest.mark.skipif(DB_URL is None, reason="TEST_DATABASE_URL no definida")


def check_repository(repository):
    product = Product(sku="TEST-001", name="Camiseta", price=Decimal("45000.00"), stock=10)

    created = CreateProduct(repository).execute(product)

    assert isinstance(created, Product)
    assert created.id == product.id
    assert created.price == Decimal("45000.00")
    assert repository.get_by_id(product.id).name == "Camiseta"
    assert repository.get_by_sku("TEST-001").id == product.id

    with pytest.raises(ProductAlreadyExistsError):
        CreateProduct(repository).execute(product)


@skip_without_db
def test_sqlmodel_repository():
    engine = create_engine(DB_URL.replace("postgresql://", "postgresql+psycopg://"))
    session = Session(engine)

    check_repository(SQLModelProductRepository(session))

    session.rollback()
    session.close()


@skip_without_db
def test_postgres_repository():
    connection = psycopg.connect(DB_URL)

    check_repository(PostgresProductRepository(connection))

    connection.rollback()
    connection.close()
