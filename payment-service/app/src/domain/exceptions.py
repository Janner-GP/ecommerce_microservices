class PaymentAlreadyExistsError(Exception):
    def __init__(self, order_id):
        super().__init__(f"La orden {order_id} ya tiene un pago registrado")


class PaymentNotFoundError(Exception):
    def __init__(self, payment_id):
        super().__init__(f"No existe el pago {payment_id}")
