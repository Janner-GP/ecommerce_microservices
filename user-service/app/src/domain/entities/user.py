"""Entidad de dominio: lo que el caso de uso conoce de un usuario.

Es una clase normal de Python. No importa SQLModel ni psycopg.
El modelo de tabla (domain/models/user.py) sigue existiendo porque
Alembic lo usa para las migraciones; los repositorios traducen entre ambos.
"""
import uuid
from enum import Enum

from app.src.shared.utils.date import utc_now


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    PENDING = "PENDING"


class User:
    def __init__(
        self,
        name,
        identification_type,
        identification_number,
        birthday_date,
        status=UserStatus.ACTIVE,
        id=None,
        created_at=None,
        updated_at=None,
    ):
        # Si no recibimos un id o unas fechas, es un usuario nuevo: los generamos.
        if id is None:
            id = uuid.uuid4()
        if created_at is None:
            created_at = utc_now()
        if updated_at is None:
            updated_at = created_at

        self.id = id
        self.name = name
        self.identification_type = identification_type
        self.identification_number = identification_number
        self.birthday_date = birthday_date
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
