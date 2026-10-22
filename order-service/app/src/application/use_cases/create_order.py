from app.src.domain.entities.order import Order
from app.src.domain.exceptions import InvalidOrderError
from app.src.domain.repositories.order_repository import OrderRepository


class CreateOrder:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order: Order) -> Order:
        # Reglas de negocio: la orden necesita ítems con cantidad positiva,
        # y el total lo calcula el sistema, no el cliente.
        if len(order.items) == 0:
            raise InvalidOrderError("La orden debe tener al menos un producto")

        total = 0
        for item in order.items:
            if item.quantity <= 0:
                raise InvalidOrderError("La cantidad de cada producto debe ser mayor que 0")
            total = total + item.subtotal()

        order.total = total

        return self.order_repository.create(order)
