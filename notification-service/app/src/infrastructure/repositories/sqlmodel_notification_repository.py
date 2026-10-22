from app.src.domain.entities.notification import Notification
from app.src.domain.models.notification import Notification as NotificationModel
from app.src.domain.repositories.notification_repository import NotificationRepository


class SQLModelNotificationRepository(NotificationRepository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, notification_id):
        model = self.session.get(NotificationModel, notification_id)

        if model is None:
            return None

        return to_domain(model)

    def create(self, notification):
        model = NotificationModel(
            id=notification.id,
            user_id=notification.user_id,
            channel=notification.channel,
            recipient=notification.recipient,
            subject=notification.subject,
            message=notification.message,
            status=notification.status,
            created_at=notification.created_at,
            sent_at=notification.sent_at,
        )
        self.session.add(model)

        # flush envía el INSERT pero NO lo confirma: el commit lo hace get_session.
        self.session.flush()
        self.session.refresh(model)

        return to_domain(model)


def to_domain(model):
    """Convierte el modelo de SQLModel en la entidad de dominio."""
    return Notification(
        id=model.id,
        user_id=model.user_id,
        channel=model.channel,
        recipient=model.recipient,
        subject=model.subject,
        message=model.message,
        status=model.status,
        created_at=model.created_at,
        sent_at=model.sent_at,
    )
