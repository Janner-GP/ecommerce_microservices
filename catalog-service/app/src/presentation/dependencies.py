"""Punto de composición: el único lugar que decide qué adaptador se usa.

El router y los casos de uso solo conocen ProductRepository.
Para pasar de SQLModel a SQL directo se cambia PERSISTENCE_ADAPTER en el .env.

scope="function" hace que el commit se ejecute ANTES de enviar la respuesta.
"""
from fastapi import Depends

from app.src.application.use_cases.create_product import CreateProduct
from app.src.application.use_cases.get_product import GetProduct
from app.src.infrastructure.database.postgres_connection import get_connection
from app.src.infrastructure.database.sqlmodel_session import get_session
from app.src.infrastructure.repositories.postgres_product_repository import (
    PostgresProductRepository,
)
from app.src.infrastructure.repositories.sqlmodel_product_repository import (
    SQLModelProductRepository,
)
from app.src.shared.config import PERSISTENCE_ADAPTER


# Opción A: SQLModel (ORM) con una sesión.
def get_sqlmodel_product_repository(session=Depends(get_session, scope="function")):
    return SQLModelProductRepository(session)


# Opción B: SQL directo con una conexión de psycopg.
def get_postgres_product_repository(connection=Depends(get_connection, scope="function")):
    return PostgresProductRepository(connection)


# Se elige una sola vez, al arrancar la aplicación.
if PERSISTENCE_ADAPTER == "postgres":
    get_product_repository = get_postgres_product_repository
else:
    get_product_repository = get_sqlmodel_product_repository


def get_create_product(product_repository=Depends(get_product_repository)):
    return CreateProduct(product_repository)


def get_get_product(product_repository=Depends(get_product_repository)):
    return GetProduct(product_repository)
