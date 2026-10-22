import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.src.domain.entities.notification import NotificationChannel, NotificationStatus
from app.src.shared.utils.date import utc_now


# Modelo de persistencia (tabla). Lo usan Alembic y SQLModelNotificationRepository.
# La entidad que maneja el caso de uso está en domain/entities/notification.py.
class Notification(SQLModel, table=True):
    __tablename__ = "ntf_notifications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # El usuario vive en user-service: aquí solo guardamos su id (sin foreign key).
    user_id: uuid.UUID = Field(index=True)

    channel: NotificationChannel
    recipient: str = Field(max_length=150)
    subject: str | None = Field(default=None, max_length=150)
    message: str
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)

    created_at: datetime = Field(default_factory=utc_now)
    sent_at: datetime | None = None
