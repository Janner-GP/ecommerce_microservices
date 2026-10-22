"""Contrato de persistencia de usuarios.

Describe lo que necesita la aplicación, no cómo se guarda.
No importa SQLModel, psycopg ni sesiones.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    def get_by_identification(self, identification_number: str) -> User | None: ...

    @abstractmethod
    def create(self, user: User) -> User: ...
