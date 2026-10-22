"""Punto de composición: el único lugar que decide qué adaptador se usa.

El router y los casos de uso solo conocen PaymentRepository.
Para pasar de SQLModel a SQL directo se cambia PERSISTENCE_ADAPTER en el .env.

scope="function" hace que el commit se ejecute ANTES de enviar la respuesta.
"""
from fastapi import Depends

from app.src.application.use_cases.create_payment import CreatePayment
from app.src.application.use_cases.get_payment import GetPayment
from app.src.infrastructure.database.postgres_connection import get_connection
from app.src.infrastructure.database.sqlmodel_session import get_session
from app.src.infrastructure.repositories.postgres_payment_repository import (
    PostgresPaymentRepository,
)
from app.src.infrastructure.repositories.sqlmodel_payment_repository import (
    SQLModelPaymentRepository,
)
from app.src.shared.config import PERSISTENCE_ADAPTER


# Opción A: SQLModel (ORM) con una sesión.
def get_sqlmodel_payment_repository(session=Depends(get_session, scope="function")):
    return SQLModelPaymentRepository(session)


# Opción B: SQL directo con una conexión de psycopg.
def get_postgres_payment_repository(connection=Depends(get_connection, scope="function")):
    return PostgresPaymentRepository(connection)


# Se elige una sola vez, al arrancar la aplicación.
if PERSISTENCE_ADAPTER == "postgres":
    get_payment_repository = get_postgres_payment_repository
else:
    get_payment_repository = get_sqlmodel_payment_repository


def get_create_payment(payment_repository=Depends(get_payment_repository)):
    return CreatePayment(payment_repository)


def get_get_payment(payment_repository=Depends(get_payment_repository)):
    return GetPayment(payment_repository)
