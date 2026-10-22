"""La misma prueba se ejecuta con los dos adaptadores: deben cumplir el mismo contrato.

Requiere una base con las migraciones aplicadas:
    TEST_DATABASE_URL=postgresql://... uv run pytest
Al final se hace rollback, así que no deja datos.
"""
import os
from datetime import date

import psycopg
import pytest
from sqlmodel import Session, create_engine

from app.src.application.use_cases.create_user import CreateUser
from app.src.domain.entities.user import User, UserStatus
from app.src.domain.exceptions import UserAlreadyExistsError
from app.src.infrastructure.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from app.src.infrastructure.repositories.sqlmodel_user_repository import (
    SQLModelUserRepository,
)

DB_URL = os.getenv("TEST_DATABASE_URL")
skip_without_db = pytest.mark.skipif(DB_URL is None, reason="TEST_DATABASE_URL no definida")


def check_repository(repository):
    user = User(
        name="Ana",
        identification_type="CC",
        identification_number="test-123",
        birthday_date=date(2000, 1, 1),
    )

    created = CreateUser(repository).execute(user)

    assert isinstance(created, User)
    assert created.id == user.id
    assert created.status == UserStatus.ACTIVE
    assert repository.get_by_id(user.id).name == "Ana"
    assert repository.get_by_identification("test-123").id == user.id

    with pytest.raises(UserAlreadyExistsError):
        CreateUser(repository).execute(user)


@skip_without_db
def test_sqlmodel_repository():
    engine = create_engine(DB_URL.replace("postgresql://", "postgresql+psycopg://"))
    session = Session(engine)

    check_repository(SQLModelUserRepository(session))

    session.rollback()
    session.close()


@skip_without_db
def test_postgres_repository():
    connection = psycopg.connect(DB_URL)

    check_repository(PostgresUserRepository(connection))

    connection.rollback()
    connection.close()
