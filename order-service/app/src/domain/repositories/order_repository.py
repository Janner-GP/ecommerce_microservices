"""Contrato de persistencia de órdenes.

Describe lo que necesita la aplicación, no cómo se guarda.
No importa SQLModel, psycopg ni sesiones.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.src.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: UUID) -> Order | None: ...

    @abstractmethod
    def create(self, order: Order) -> Order: ...
