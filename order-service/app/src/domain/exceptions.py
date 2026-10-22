class InvalidOrderError(Exception):
    pass


class OrderNotFoundError(Exception):
    def __init__(self, order_id):
        super().__init__(f"No existe la orden {order_id}")
