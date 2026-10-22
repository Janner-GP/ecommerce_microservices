"""El caso de uso se prueba sin base de datos: basta un repositorio en memoria."""
import uuid
from decimal import Decimal

import pytest

from app.src.application.use_cases.create_payment import CreatePayment
from app.src.application.use_cases.get_payment import GetPayment
from app.src.domain.entities.payment import Payment, PaymentMethod, PaymentStatus
from app.src.domain.exceptions import PaymentAlreadyExistsError, PaymentNotFoundError
from app.src.domain.repositories.payment_repository import PaymentRepository


class InMemoryPaymentRepository(PaymentRepository):
    def __init__(self):
        self.payments = []

    def get_by_id(self, payment_id):
        for payment in self.payments:
            if payment.id == payment_id:
                return payment
        return None

    def get_by_order_id(self, order_id):
        for payment in self.payments:
            if payment.order_id == order_id:
                return payment
        return None

    def create(self, payment):
        self.payments.append(payment)
        return payment


ORDER_ID = uuid.uuid4()


def new_payment():
    return Payment(order_id=ORDER_ID, amount=Decimal("90000.00"), method=PaymentMethod.CARD)


def test_crea_pago_pendiente():
    repository = InMemoryPaymentRepository()

    payment = CreatePayment(repository).execute(new_payment())

    assert payment.status == PaymentStatus.PENDING
    assert repository.get_by_id(payment.id) is payment


def test_rechaza_segundo_pago_de_la_misma_orden():
    repository = InMemoryPaymentRepository()
    CreatePayment(repository).execute(new_payment())

    with pytest.raises(PaymentAlreadyExistsError):
        CreatePayment(repository).execute(new_payment())


def test_get_payment_inexistente():
    repository = InMemoryPaymentRepository()

    with pytest.raises(PaymentNotFoundError):
        GetPayment(repository).execute(uuid.uuid4())
