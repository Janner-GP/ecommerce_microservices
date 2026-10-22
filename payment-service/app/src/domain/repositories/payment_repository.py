"""Contrato de persistencia de pagos.

Describe lo que necesita la aplicación, no cómo se guarda.
No importa SQLModel, psycopg ni sesiones.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.src.domain.entities.payment import Payment


class PaymentRepository(ABC):
    @abstractmethod
    def get_by_id(self, payment_id: UUID) -> Payment | None: ...

    @abstractmethod
    def get_by_order_id(self, order_id: UUID) -> Payment | None: ...

    @abstractmethod
    def create(self, payment: Payment) -> Payment: ...
