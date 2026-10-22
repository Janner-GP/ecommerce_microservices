"""El caso de uso se prueba sin base de datos: basta un repositorio en memoria."""
from decimal import Decimal

import pytest

from app.src.application.use_cases.create_product import CreateProduct
from app.src.application.use_cases.get_product import GetProduct
from app.src.domain.entities.product import Product
from app.src.domain.exceptions import ProductAlreadyExistsError, ProductNotFoundError
from app.src.domain.repositories.product_repository import ProductRepository


class InMemoryProductRepository(ProductRepository):
    def __init__(self):
        self.products = []

    def get_by_id(self, product_id):
        for product in self.products:
            if product.id == product_id:
                return product
        return None

    def get_by_sku(self, sku):
        for product in self.products:
            if product.sku == sku:
                return product
        return None

    def create(self, product):
        self.products.append(product)
        return product


def new_product():
    return Product(sku="CAM-001", name="Camiseta", price=Decimal("45000.00"), stock=10)


def test_crea_producto():
    repository = InMemoryProductRepository()

    product = CreateProduct(repository).execute(new_product())

    assert repository.get_by_id(product.id) is product


def test_rechaza_sku_repetido():
    repository = InMemoryProductRepository()
    CreateProduct(repository).execute(new_product())

    with pytest.raises(ProductAlreadyExistsError):
        CreateProduct(repository).execute(new_product())


def test_get_product_inexistente():
    repository = InMemoryProductRepository()

    with pytest.raises(ProductNotFoundError):
        GetProduct(repository).execute(new_product().id)
