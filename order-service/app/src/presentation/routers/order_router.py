from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.src.domain.entities.order import Order, OrderItem
from app.src.domain.exceptions import InvalidOrderError, OrderNotFoundError
from app.src.presentation.dependencies import get_create_order, get_get_order
from app.src.presentation.schemas.order_schemas import (
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


# El router solo traduce entre HTTP y el caso de uso.
# No ejecuta SQL ni aplica reglas de negocio.
@router.post("", status_code=201)
def create_order(payload: OrderCreate, use_case=Depends(get_create_order)) -> OrderResponse:
    items = []
    for item in payload.items:
        items.append(
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
        )

    order = Order(user_id=payload.user_id, items=items)

    try:
        created = use_case.execute(order)
    except InvalidOrderError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return to_response(created)


@router.get("/{order_id}")
def get_order(order_id: UUID, use_case=Depends(get_get_order)) -> OrderResponse:
    try:
        order = use_case.execute(order_id)
    except OrderNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return to_response(order)


def to_response(order):
    """Convierte la entidad de dominio en la respuesta HTTP."""
    items = []
    for item in order.items:
        items.append(
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
        )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total=order.total,
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
