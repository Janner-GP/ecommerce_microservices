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

from app.src.application.use_cases.create_payment import CreatePayment
from app.src.domain.entities.payment import Payment, PaymentMethod, PaymentStatus
from app.src.domain.exceptions import PaymentAlreadyExistsError
from app.src.infrastructure.repositories.postgres_payment_repository import (
    PostgresPaymentRepository,
)
from app.src.infrastructure.repositories.sqlmodel_payment_repository import (
    SQLModelPaymentRepository,
)

DB_URL = os.getenv("TEST_DATABASE_URL")
skip_without_db = pytest.mark.skipif(DB_URL is None, reason="TEST_DATABASE_URL no definida")


def check_repository(repository):
    order_id = uuid.uuid4()
    payment = Payment(order_id=order_id, amount=Decimal("90000.00"), method=PaymentMethod.PSE)

    created = CreatePayment(repository).execute(payment)

    assert isinstance(created, Payment)
    assert created.method == PaymentMethod.PSE
    assert created.status == PaymentStatus.PENDING
    assert repository.get_by_id(payment.id).amount == Decimal("90000.00")
    assert repository.get_by_order_id(order_id).id == payment.id

    with pytest.raises(PaymentAlreadyExistsError):
        CreatePayment(repository).execute(payment)


@skip_without_db
def test_sqlmodel_repository():
    engine = create_engine(DB_URL.replace("postgresql://", "postgresql+psycopg://"))
    session = Session(engine)

    check_repository(SQLModelPaymentRepository(session))

    session.rollback()
    session.close()


@skip_without_db
def test_postgres_repository():
    connection = psycopg.connect(DB_URL)

    check_repository(PostgresPaymentRepository(connection))

    connection.rollback()
    connection.close()
