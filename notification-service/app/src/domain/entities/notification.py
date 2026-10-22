"""Entidad de dominio: lo que el caso de uso conoce de una notificación.

Es una clase normal de Python. No importa SQLModel ni psycopg.
"""
import uuid
from enum import Enum

from app.src.shared.utils.date import utc_now


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class Notification:
    def __init__(
        self,
        user_id,
        channel,
        recipient,
        message,
        subject=None,
        status=NotificationStatus.PENDING,
        id=None,
        created_at=None,
        sent_at=None,
    ):
        # Si no recibimos un id o una fecha, es una notificación nueva: los generamos.
        if id is None:
            id = uuid.uuid4()
        if created_at is None:
            created_at = utc_now()

        self.id = id
        self.user_id = user_id
        self.channel = channel
        self.recipient = recipient
        self.subject = subject
        self.message = message
        self.status = status
        self.created_at = created_at
        self.sent_at = sent_at
