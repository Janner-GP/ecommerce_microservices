"""Punto de composición: el único lugar que decide qué adaptador se usa.

El router y los casos de uso solo conocen UserRepository.
Para pasar de SQLModel a SQL directo se cambia PERSISTENCE_ADAPTER en el .env
(los dos adaptadores usan la misma tabla y el mismo DATABASE_URL).

scope="function" hace que el commit se ejecute ANTES de enviar la respuesta.
Sin él, FastAPI responde primero y confirma después: si el commit fallara,
el cliente ya habría recibido un 201.
"""
from fastapi import Depends

from app.src.application.use_cases.create_user import CreateUser
from app.src.application.use_cases.get_user import GetUser
from app.src.infrastructure.database.postgres_connection import get_connection
from app.src.infrastructure.database.sqlmodel_session import get_session
from app.src.infrastructure.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from app.src.infrastructure.repositories.sqlmodel_user_repository import (
    SQLModelUserRepository,
)
from app.src.shared.config import PERSISTENCE_ADAPTER


# Opción A: SQLModel (ORM) con una sesión.
def get_sqlmodel_user_repository(session=Depends(get_session, scope="function")):
    return SQLModelUserRepository(session)


# Opción B: SQL directo con una conexión de psycopg.
def get_postgres_user_repository(connection=Depends(get_connection, scope="function")):
    return PostgresUserRepository(connection)


# Se elige una sola vez, al arrancar la aplicación.
if PERSISTENCE_ADAPTER == "postgres":
    get_user_repository = get_postgres_user_repository
else:
    get_user_repository = get_sqlmodel_user_repository


def get_create_user(user_repository=Depends(get_user_repository)):
    return CreateUser(user_repository)


def get_get_user(user_repository=Depends(get_user_repository)):
    return GetUser(user_repository)
