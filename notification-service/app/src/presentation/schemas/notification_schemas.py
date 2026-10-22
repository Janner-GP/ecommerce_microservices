"""Contrato HTTP: no cambia aunque cambie el adaptador de persistencia."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.src.domain.entities.notification import NotificationChannel, NotificationStatus


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    channel: NotificationChannel
    recipient: str = Field(max_length=150)
    subject: str | None = Field(default=None, max_length=150)
    message: str


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    channel: NotificationChannel
    recipient: str
    subject: str | None
    message: str
    status: NotificationStatus
    created_at: datetime
    sent_at: datetime | None
