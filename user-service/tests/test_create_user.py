"""El caso de uso se prueba sin base de datos: basta un repositorio en memoria."""
from datetime import date

import pytest

from app.src.application.use_cases.create_user import CreateUser
from app.src.application.use_cases.get_user import GetUser
from app.src.domain.entities.user import User
from app.src.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.src.domain.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users = []

    def get_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def get_by_identification(self, identification_number):
        for user in self.users:
            if user.identification_number == identification_number:
                return user
        return None

    def create(self, user):
        self.users.append(user)
        return user


def new_user():
    return User(
        name="Ana",
        identification_type="CC",
        identification_number="123",
        birthday_date=date(2000, 1, 1),
    )


def test_crea_usuario():
    repository = InMemoryUserRepository()

    user = CreateUser(repository).execute(new_user())

    assert repository.get_by_id(user.id) is user


def test_rechaza_identificacion_repetida():
    repository = InMemoryUserRepository()
    CreateUser(repository).execute(new_user())

    with pytest.raises(UserAlreadyExistsError):
        CreateUser(repository).execute(new_user())


def test_get_user_inexistente():
    repository = InMemoryUserRepository()

    with pytest.raises(UserNotFoundError):
        GetUser(repository).execute(new_user().id)
