from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.src.domain.entities.payment import Payment
from app.src.domain.exceptions import PaymentAlreadyExistsError, PaymentNotFoundError
from app.src.presentation.dependencies import get_create_payment, get_get_payment
from app.src.presentation.schemas.payment_schemas import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/payments", tags=["payments"])


# El router solo traduce entre HTTP y el caso de uso.
# No ejecuta SQL ni aplica reglas de negocio.
@router.post("", status_code=201)
def create_payment(payload: PaymentCreate, use_case=Depends(get_create_payment)) -> PaymentResponse:
    payment = Payment(
        order_id=payload.order_id,
        amount=payload.amount,
        method=payload.method,
    )

    try:
        created = use_case.execute(payment)
    except PaymentAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return to_response(created)


@router.get("/{payment_id}")
def get_payment(payment_id: UUID, use_case=Depends(get_get_payment)) -> PaymentResponse:
    try:
        payment = use_case.execute(payment_id)
    except PaymentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return to_response(payment)


def to_response(payment):
    """Convierte la entidad de dominio en la respuesta HTTP."""
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        method=payment.method,
        status=payment.status,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )
