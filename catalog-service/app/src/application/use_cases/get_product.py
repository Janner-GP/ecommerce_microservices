from uuid import UUID

from app.src.domain.entities.product import Product
from app.src.domain.exceptions import ProductNotFoundError
from app.src.domain.repositories.product_repository import ProductRepository


class GetProduct:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def execute(self, product_id: UUID) -> Product:
        product = self.product_repository.get_by_id(product_id)

        if product is None:
            raise ProductNotFoundError(product_id)

        return product
