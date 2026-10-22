from app.src.domain.entities.product import Product
from app.src.domain.exceptions import ProductAlreadyExistsError
from app.src.domain.repositories.product_repository import ProductRepository


class CreateProduct:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def execute(self, product: Product) -> Product:
        existing = self.product_repository.get_by_sku(product.sku)

        if existing is not None:
            raise ProductAlreadyExistsError(product.sku)

        return self.product_repository.create(product)
