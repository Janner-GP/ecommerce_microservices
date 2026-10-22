from app.src.domain.entities.payment import Payment
from app.src.domain.exceptions import PaymentAlreadyExistsError
from app.src.domain.repositories.payment_repository import PaymentRepository


class CreatePayment:
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    def execute(self, payment: Payment) -> Payment:
        # Regla de negocio: una orden solo puede tener un pago.
        existing = self.payment_repository.get_by_order_id(payment.order_id)

        if existing is not None:
            raise PaymentAlreadyExistsError(payment.order_id)

        return self.payment_repository.create(payment)
