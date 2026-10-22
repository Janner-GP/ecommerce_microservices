"""La misma prueba se ejecuta con los dos adaptadores: deben cumplir el mismo contrato.

Requiere una base con las migraciones aplicadas:
    TEST_DATABASE_URL=postgresql://... uv run pytest
Al final se hace rollback, así que no deja datos.
"""
import os
import uuid

import psycopg
import pytest
from sqlmodel import Session, create_engine

from app.src.application.use_cases.create_notification import CreateNotification
from app.src.domain.entities.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)
from app.src.infrastructure.repositories.postgres_notification_repository import (
    PostgresNotificationRepository,
)
from app.src.infrastructure.repositories.sqlmodel_notification_repository import (
    SQLModelNotificationRepository,
)

DB_URL = os.getenv("TEST_DATABASE_URL")
skip_without_db = pytest.mark.skipif(DB_URL is None, reason="TEST_DATABASE_URL no definida")


def check_repository(repository):
    notification = Notification(
        user_id=uuid.uuid4(),
        channel=NotificationChannel.EMAIL,
        recipient="ana@correo.com",
        subject="Tu orden",
        message="Tu orden fue creada",
    )

    created = CreateNotification(repository).execute(notification)

    assert isinstance(created, Notification)
    assert created.channel == NotificationChannel.EMAIL
    assert created.status == NotificationStatus.PENDING
    assert created.sent_at is None
    assert repository.get_by_id(notification.id).recipient == "ana@correo.com"


@skip_without_db
def test_sqlmodel_repository():
    engine = create_engine(DB_URL.replace("postgresql://", "postgresql+psycopg://"))
    session = Session(engine)

    check_repository(SQLModelNotificationRepository(session))

    session.rollback()
    session.close()


@skip_without_db
def test_postgres_repository():
    connection = psycopg.connect(DB_URL)

    check_repository(PostgresNotificationRepository(connection))

    connection.rollback()
    connection.close()
