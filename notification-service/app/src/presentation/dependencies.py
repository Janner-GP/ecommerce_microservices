"""Punto de composición: el único lugar que decide qué adaptador se usa.

El router y los casos de uso solo conocen NotificationRepository.
Para pasar de SQLModel a SQL directo se cambia PERSISTENCE_ADAPTER en el .env.

scope="function" hace que el commit se ejecute ANTES de enviar la respuesta.
"""
from fastapi import Depends

from app.src.application.use_cases.create_notification import CreateNotification
from app.src.application.use_cases.get_notification import GetNotification
from app.src.infrastructure.database.postgres_connection import get_connection
from app.src.infrastructure.database.sqlmodel_session import get_session
from app.src.infrastructure.repositories.postgres_notification_repository import (
    PostgresNotificationRepository,
)
from app.src.infrastructure.repositories.sqlmodel_notification_repository import (
    SQLModelNotificationRepository,
)
from app.src.shared.config import PERSISTENCE_ADAPTER


# Opción A: SQLModel (ORM) con una sesión.
def get_sqlmodel_notification_repository(session=Depends(get_session, scope="function")):
    return SQLModelNotificationRepository(session)


# Opción B: SQL directo con una conexión de psycopg.
def get_postgres_notification_repository(connection=Depends(get_connection, scope="function")):
    return PostgresNotificationRepository(connection)


# Se elige una sola vez, al arrancar la aplicación.
if PERSISTENCE_ADAPTER == "postgres":
    get_notification_repository = get_postgres_notification_repository
else:
    get_notification_repository = get_sqlmodel_notification_repository


def get_create_notification(notification_repository=Depends(get_notification_repository)):
    return CreateNotification(notification_repository)


def get_get_notification(notification_repository=Depends(get_notification_repository)):
    return GetNotification(notification_repository)
