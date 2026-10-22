from app.src.domain.entities.notification import Notification, NotificationChannel
from app.src.domain.exceptions import InvalidNotificationError
from app.src.domain.repositories.notification_repository import NotificationRepository


class CreateNotification:
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    def execute(self, notification: Notification) -> Notification:
        # Reglas de negocio de los correos.
        if notification.channel == NotificationChannel.EMAIL:
            if "@" not in notification.recipient:
                raise InvalidNotificationError("El destinatario no es un correo válido")
            if not notification.subject:
                raise InvalidNotificationError("Un correo necesita asunto")

        return self.notification_repository.create(notification)
