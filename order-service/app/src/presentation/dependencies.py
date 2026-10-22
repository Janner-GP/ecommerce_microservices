"""Punto de composición: el único lugar que decide qué adaptador se usa.

El router y los casos de uso solo conocen OrderRepository.
Para pasar de SQLModel a SQL directo se cambia PERSISTENCE_ADAPTER en el .env.

scope="function" hace que el commit se ejecute ANTES de enviar la respuesta.
"""
from fastapi import Depends

from app.src.application.use_cases.create_order import CreateOrder
from app.src.application.use_cases.get_order import GetOrder
from app.src.infrastructure.database.postgres_connection import get_connection
from app.src.infrastructure.database.sqlmodel_session import get_session
from app.src.infrastructure.repositories.postgres_order_repository import (
    PostgresOrderRepository,
)
from app.src.infrastructure.repositories.sqlmodel_order_repository import (
    SQLModelOrderRepository,
)
from app.src.shared.config import PERSISTENCE_ADAPTER


# Opción A: SQLModel (ORM) con una sesión.
def get_sqlmodel_order_repository(session=Depends(get_session, scope="function")):
    return SQLModelOrderRepository(session)


# Opción B: SQL directo con una conexión de psycopg.
def get_postgres_order_repository(connection=Depends(get_connection, scope="function")):
    return PostgresOrderRepository(connection)


# Se elige una sola vez, al arrancar la aplicación.
if PERSISTENCE_ADAPTER == "postgres":
    get_order_repository = get_postgres_order_repository
else:
    get_order_repository = get_sqlmodel_order_repository


def get_create_order(order_repository=Depends(get_order_repository)):
    return CreateOrder(order_repository)


def get_get_order(order_repository=Depends(get_order_repository)):
    return GetOrder(order_repository)
