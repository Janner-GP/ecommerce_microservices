"""El caso de uso se prueba sin base de datos: basta un repositorio en memoria."""
import uuid
from decimal import Decimal

import pytest

from app.src.application.use_cases.create_order import CreateOrder
from app.src.application.use_cases.get_order import GetOrder
from app.src.domain.entities.order import Order, OrderItem, OrderStatus
from app.src.domain.exceptions import InvalidOrderError, OrderNotFoundError
from app.src.domain.repositories.order_repository import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self.orders = []

    def get_by_id(self, order_id):
        for order in self.orders:
            if order.id == order_id:
                return order
        return None

    def create(self, order):
        self.orders.append(order)
        return order


def test_crea_orden_y_calcula_total():
    repository = InMemoryOrderRepository()
    order = Order(
        user_id=uuid.uuid4(),
        items=[
            OrderItem(product_id=uuid.uuid4(), quantity=2, unit_price=Decimal("45000.00")),
            OrderItem(product_id=uuid.uuid4(), quantity=1, unit_price=Decimal("10000.00")),
        ],
    )

    created = CreateOrder(repository).execute(order)

    assert created.total == Decimal("100000.00")
    assert created.status == OrderStatus.PENDING
    assert repository.get_by_id(created.id) is created


def test_rechaza_orden_sin_items():
    order = Order(user_id=uuid.uuid4(), items=[])

    with pytest.raises(InvalidOrderError):
        CreateOrder(InMemoryOrderRepository()).execute(order)


def test_rechaza_cantidad_cero():
    order = Order(
        user_id=uuid.uuid4(),
        items=[OrderItem(product_id=uuid.uuid4(), quantity=0, unit_price=Decimal("1000"))],
    )

    with pytest.raises(InvalidOrderError):
        CreateOrder(InMemoryOrderRepository()).execute(order)


def test_get_order_inexistente():
    with pytest.raises(OrderNotFoundError):
        GetOrder(InMemoryOrderRepository()).execute(uuid.uuid4())
