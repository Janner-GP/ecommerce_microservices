from sqlmodel import select

from app.src.domain.entities.payment import Payment
from app.src.domain.models.payment import Payment as PaymentModel
from app.src.domain.repositories.payment_repository import PaymentRepository


class SQLModelPaymentRepository(PaymentRepository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, payment_id):
        model = self.session.get(PaymentModel, payment_id)

        if model is None:
            return None

        return to_domain(model)

    def get_by_order_id(self, order_id):
        statement = select(PaymentModel).where(PaymentModel.order_id == order_id)
        model = self.session.exec(statement).first()

        if model is None:
            return None

        return to_domain(model)

    def create(self, payment):
        model = PaymentModel(
            id=payment.id,
            order_id=payment.order_id,
            amount=payment.amount,
            method=payment.method,
            status=payment.status,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
        self.session.add(model)

        # flush envía el INSERT pero NO lo confirma: el commit lo hace get_session.
        self.session.flush()
        self.session.refresh(model)

        return to_domain(model)


def to_domain(model):
    """Convierte el modelo de SQLModel en la entidad de dominio."""
    return Payment(
        id=model.id,
        order_id=model.order_id,
        amount=model.amount,
        method=model.method,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
