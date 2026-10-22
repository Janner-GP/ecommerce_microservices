"""Contrato de persistencia de notificaciones.

Describe lo que necesita la aplicación, no cómo se guarda.
No importa SQLModel, psycopg ni sesiones.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.src.domain.entities.notification import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def get_by_id(self, notification_id: UUID) -> Notification | None: ...

    @abstractmethod
    def create(self, notification: Notification) -> Notification: ...
