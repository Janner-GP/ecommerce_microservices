from datetime import date, datetime
import uuid

from sqlmodel import SQLModel, Field
from app.src.domain.entities.user import UserStatus
from app.src.shared.utils.date import utc_now


# Modelo de persistencia (tabla). Lo usan Alembic y SQLModelUserRepository.
# La entidad que maneja el caso de uso está en domain/entities/user.py.
class User(SQLModel, table=True):
    __tablename__ = "usr_users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    name: str = Field(index=True, max_length=150)
    identification_type: str = Field(max_length=30)
    identification_number: str = Field(
        index=True,
        max_length=50,
    )

    # Una fecha de nacimiento no necesita almacenar hora.
    birthday_date: date

    status: UserStatus = Field(default=UserStatus.ACTIVE)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)