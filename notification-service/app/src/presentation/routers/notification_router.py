from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.src.domain.entities.notification import Notification
from app.src.domain.exceptions import InvalidNotificationError, NotificationNotFoundError
from app.src.presentation.dependencies import get_create_notification, get_get_notification
from app.src.presentation.schemas.notification_schemas import (
    NotificationCreate,
    NotificationResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


# El router solo traduce entre HTTP y el caso de uso.
# No ejecuta SQL ni aplica reglas de negocio.
@router.post("", status_code=201)
def create_notification(
    payload: NotificationCreate,
    use_case=Depends(get_create_notification),
) -> NotificationResponse:
    notification = Notification(
        user_id=payload.user_id,
        channel=payload.channel,
        recipient=payload.recipient,
        subject=payload.subject,
        message=payload.message,
    )

    try:
        created = use_case.execute(notification)
    except InvalidNotificationError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return to_response(created)


@router.get("/{notification_id}")
def get_notification(
    notification_id: UUID,
    use_case=Depends(get_get_notification),
) -> NotificationResponse:
    try:
        notification = use_case.execute(notification_id)
    except NotificationNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return to_response(notification)


def to_response(notification):
    """Convierte la entidad de dominio en la respuesta HTTP."""
    return NotificationResponse(
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
