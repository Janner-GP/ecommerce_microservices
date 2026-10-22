from app.src.domain.entities.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)
from app.src.domain.repositories.notification_repository import NotificationRepository


class PostgresNotificationRepository(NotificationRepository):
    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, notification_id):
        # %s es un parámetro de psycopg, no formateo de texto:
        # el valor viaja separado de la consulta, así no hay inyección SQL.
        row = self.connection.execute(
            """
            SELECT id, user_id, channel, recipient, subject,
                   message, status, created_at, sent_at
            FROM ntf_notifications
            WHERE id = %s
            """,
            (notification_id,),
        ).fetchone()

        if row is None:
            return None

        return to_domain(row)

    def create(self, notification):
        # El INSERT queda pendiente hasta que get_connection haga commit.
        row = self.connection.execute(
            """
            INSERT INTO ntf_notifications (
                id, user_id, channel, recipient, subject,
                message, status, created_at, sent_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, channel, recipient, subject,
                      message, status, created_at, sent_at
            """,
            (
                notification.id,
                notification.user_id,
                notification.channel.value,
                notification.recipient,
                notification.subject,
                notification.message,
                notification.status.value,
                notification.created_at,
                notification.sent_at,
            ),
        ).fetchone()

        return to_domain(row)


def to_domain(row):
    """Convierte la fila cruda de PostgreSQL en la entidad de dominio."""
    return Notification(
        id=row[0],
        user_id=row[1],
        channel=NotificationChannel(row[2]),
        recipient=row[3],
        subject=row[4],
        message=row[5],
        status=NotificationStatus(row[6]),
        created_at=row[7],
        sent_at=row[8],
    )
