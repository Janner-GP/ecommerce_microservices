"""Entidad de dominio: lo que el caso de uso conoce de un producto.

Es una clase normal de Python. No importa SQLModel ni psycopg.
"""
import uuid

from app.src.shared.utils.date import utc_now


class Product:
    def __init__(
        self,
        sku,
        name,
        price,
        stock=0,
        description=None,
        category_id=None,
        is_active=True,
        id=None,
        created_at=None,
        updated_at=None,
    ):
        # Si no recibimos un id o unas fechas, es un producto nuevo: los generamos.
        if id is None:
            id = uuid.uuid4()
        if created_at is None:
            created_at = utc_now()
        if updated_at is None:
            updated_at = created_at

        self.id = id
        self.sku = sku
        self.name = name
        self.price = price
        self.stock = stock
        self.description = description
        self.category_id = category_id
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
