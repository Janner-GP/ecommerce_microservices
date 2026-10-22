class ProductAlreadyExistsError(Exception):
    def __init__(self, sku):
        super().__init__(f"Ya existe un producto con el SKU {sku}")


class ProductNotFoundError(Exception):
    def __init__(self, product_id):
        super().__init__(f"No existe el producto {product_id}")
