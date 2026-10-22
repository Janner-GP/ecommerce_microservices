from sqlmodel import select

from app.src.domain.entities.order import Order, OrderItem
from app.src.domain.models.order import Order as OrderModel
from app.src.domain.models.order_item import OrderItem as OrderItemModel
from app.src.domain.repositories.order_repository import OrderRepository


class SQLModelOrderRepository(OrderRepository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, order_id):
        order_model = self.session.get(OrderModel, order_id)

        if order_model is None:
            return None

        statement = select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        item_models = self.session.exec(statement).all()

        return to_domain(order_model, item_models)

    def create(self, order):
        order_model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total=order.total,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        self.session.add(order_model)

        # Primero se envía la orden, porque los ítems la referencian.
        self.session.flush()

        for item in order.items:
            item_model = OrderItemModel(
                id=item.id,
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            self.session.add(item_model)

        # flush envía los INSERT pero NO los confirma: el commit lo hace get_session.
        # Si algo falla, el rollback deshace la orden y los ítems juntos.
        self.session.flush()

        return self.get_by_id(order.id)


def to_domain(order_model, item_models):
    """Convierte los modelos de SQLModel en la entidad de dominio."""
    items = []
    for item_model in item_models:
        items.append(
            OrderItem(
                id=item_model.id,
                product_id=item_model.product_id,
                quantity=item_model.quantity,
                unit_price=item_model.unit_price,
            )
        )

    return Order(
        id=order_model.id,
        user_id=order_model.user_id,
        items=items,
        status=order_model.status,
        total=order_model.total,
        created_at=order_model.created_at,
        updated_at=order_model.updated_at,
    )
