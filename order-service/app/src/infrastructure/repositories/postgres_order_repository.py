from app.src.domain.entities.order import Order, OrderItem, OrderStatus
from app.src.domain.repositories.order_repository import OrderRepository


class PostgresOrderRepository(OrderRepository):
    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, order_id):
        # %s es un parámetro de psycopg, no formateo de texto:
        # el valor viaja separado de la consulta, así no hay inyección SQL.
        order_row = self.connection.execute(
            """
            SELECT id, user_id, status, total, created_at, updated_at
            FROM ord_orders
            WHERE id = %s
            """,
            (order_id,),
        ).fetchone()

        if order_row is None:
            return None

        item_rows = self.connection.execute(
            """
            SELECT id, product_id, quantity, unit_price
            FROM ord_order_items
            WHERE order_id = %s
            """,
            (order_id,),
        ).fetchall()

        return to_domain(order_row, item_rows)

    def create(self, order):
        # Los INSERT quedan pendientes hasta que get_connection haga commit.
        # Si algo falla, el rollback deshace la orden y los ítems juntos.
        self.connection.execute(
            """
            INSERT INTO ord_orders (id, user_id, status, total, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                order.id,
                order.user_id,
                order.status.value,
                order.total,
                order.created_at,
                order.updated_at,
            ),
        )

        for item in order.items:
            self.connection.execute(
                """
                INSERT INTO ord_order_items (id, order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (item.id, order.id, item.product_id, item.quantity, item.unit_price),
            )

        return self.get_by_id(order.id)


def to_domain(order_row, item_rows):
    """Convierte las filas crudas de PostgreSQL en la entidad de dominio."""
    items = []
    for row in item_rows:
        items.append(
            OrderItem(
                id=row[0],
                product_id=row[1],
                quantity=row[2],
                unit_price=row[3],
            )
        )

    return Order(
        id=order_row[0],
        user_id=order_row[1],
        items=items,
        status=OrderStatus(order_row[2]),
        total=order_row[3],
        created_at=order_row[4],
        updated_at=order_row[5],
    )
