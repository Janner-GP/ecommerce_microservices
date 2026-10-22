from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.src.domain.entities.user import User
from app.src.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.src.presentation.dependencies import get_create_user, get_get_user
from app.src.presentation.schemas.user_schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


# El router solo traduce entre HTTP y el caso de uso.
# No ejecuta SQL ni aplica reglas de negocio.
@router.post("", status_code=201)
def create_user(payload: UserCreate, use_case=Depends(get_create_user)) -> UserResponse:
    user = User(
        name=payload.name,
        identification_type=payload.identification_type,
        identification_number=payload.identification_number,
        birthday_date=payload.birthday_date,
    )

    try:
        created = use_case.execute(user)
    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return to_response(created)


@router.get("/{user_id}")
def get_user(user_id: UUID, use_case=Depends(get_get_user)) -> UserResponse:
    try:
        user = use_case.execute(user_id)
    except UserNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return to_response(user)


def to_response(user):
    """Convierte la entidad de dominio en la respuesta HTTP."""
    return UserResponse(
        id=user.id,
        name=user.name,
        identification_type=user.identification_type,
        identification_number=user.identification_number,
        birthday_date=user.birthday_date,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
