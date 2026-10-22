"""Contrato de persistencia de productos.

Describe lo que necesita la aplicación, no cómo se guarda.
No importa SQLModel, psycopg ni sesiones.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.src.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Product | None: ...

    @abstractmethod
    def get_by_sku(self, sku: str) -> Product | None: ...

    @abstractmethod
    def create(self, product: Product) -> Product: ...
