"""El caso de uso se prueba sin base de datos: basta un repositorio en memoria."""
import uuid

import pytest

from app.src.application.use_cases.create_notification import CreateNotification
from app.src.application.use_cases.get_notification import GetNotification
from app.src.domain.entities.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)
from app.src.domain.exceptions import InvalidNotificationError, NotificationNotFoundError
from app.src.domain.repositories.notification_repository import NotificationRepository


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self):
        self.notifications = []

    def get_by_id(self, notification_id):
        for notification in self.notifications:
            if notification.id == notification_id:
                return notification
        return None

    def create(self, notification):
        self.notifications.append(notification)
        return notification


def test_crea_correo_pendiente():
    repository = InMemoryNotificationRepository()
    email = Notification(
        user_id=uuid.uuid4(),
        channel=NotificationChannel.EMAIL,
        recipient="ana@correo.com",
        subject="Tu orden",
        message="Tu orden fue creada",
    )

    created = CreateNotification(repository).execute(email)

    assert created.status == NotificationStatus.PENDING
    assert repository.get_by_id(created.id) is created


def test_rechaza_correo_sin_arroba():
    email = Notification(
        user_id=uuid.uuid4(),
        channel=NotificationChannel.EMAIL,
        recipient="ana",
        subject="Tu orden",
        message="Hola",
    )

    with pytest.raises(InvalidNotificationError):
        CreateNotification(InMemoryNotificationRepository()).execute(email)


def test_rechaza_correo_sin_asunto():
    email = Notification(
        user_id=uuid.uuid4(),
        channel=NotificationChannel.EMAIL,
        recipient="ana@correo.com",
        message="Hola",
    )

    with pytest.raises(InvalidNotificationError):
        CreateNotification(InMemoryNotificationRepository()).execute(email)


def test_sms_no_necesita_asunto():
    sms = Notification(
        user_id=uuid.uuid4(),
        channel=NotificationChannel.SMS,
        recipient="3001234567",
        message="Tu orden fue creada",
    )

    created = CreateNotification(InMemoryNotificationRepository()).execute(sms)

    assert created.subject is None


def test_get_notification_inexistente():
    with pytest.raises(NotificationNotFoundError):
        GetNotification(InMemoryNotificationRepository()).execute(uuid.uuid4())
