from uuid import UUID

from app.src.domain.entities.order import Order
from app.src.domain.exceptions import OrderNotFoundError
from app.src.domain.repositories.order_repository import OrderRepository


class GetOrder:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_id: UUID) -> Order:
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        return order
