from app.src.domain.entities.payment import Payment, PaymentMethod, PaymentStatus
from app.src.domain.repositories.payment_repository import PaymentRepository


class PostgresPaymentRepository(PaymentRepository):
    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, payment_id):
        row = self.connection.execute(
            """
            SELECT id, order_id, amount, method, status, created_at, updated_at
            FROM pym_payments
            WHERE id = %s
            """,
            (payment_id,),
        ).fetchone()

        if row is None:
            return None

        return to_domain(row)

    def get_by_order_id(self, order_id):
        # %s es un parámetro de psycopg, no formateo de texto:
        # el valor viaja separado de la consulta, así no hay inyección SQL.
        row = self.connection.execute(
            """
            SELECT id, order_id, amount, method, status, created_at, updated_at
            FROM pym_payments
            WHERE order_id = %s
            """,
            (order_id,),
        ).fetchone()

        if row is None:
            return None

        return to_domain(row)

    def create(self, payment):
        # El INSERT queda pendiente hasta que get_connection haga commit.
        row = self.connection.execute(
            """
            INSERT INTO pym_payments (
                id, order_id, amount, method, status, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, order_id, amount, method, status, created_at, updated_at
            """,
            (
                payment.id,
                payment.order_id,
                payment.amount,
                payment.method.value,
                payment.status.value,
                payment.created_at,
                payment.updated_at,
            ),
        ).fetchone()

        return to_domain(row)


def to_domain(row):
    """Convierte la fila cruda de PostgreSQL en la entidad de dominio."""
    return Payment(
        id=row[0],
        order_id=row[1],
        amount=row[2],
        method=PaymentMethod(row[3]),
        status=PaymentStatus(row[4]),
        created_at=row[5],
        updated_at=row[6],
    )
