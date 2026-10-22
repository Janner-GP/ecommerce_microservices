from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.src.domain.entities.product import Product
from app.src.domain.exceptions import ProductAlreadyExistsError, ProductNotFoundError
from app.src.presentation.dependencies import get_create_product, get_get_product
from app.src.presentation.schemas.product_schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


# El router solo traduce entre HTTP y el caso de uso.
# No ejecuta SQL ni aplica reglas de negocio.
@router.post("", status_code=201)
def create_product(payload: ProductCreate, use_case=Depends(get_create_product)) -> ProductResponse:
    product = Product(
        sku=payload.sku,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        category_id=payload.category_id,
    )

    try:
        created = use_case.execute(product)
    except ProductAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return to_response(created)


@router.get("/{product_id}")
def get_product(product_id: UUID, use_case=Depends(get_get_product)) -> ProductResponse:
    try:
        product = use_case.execute(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return to_response(product)


def to_response(product):
    """Convierte la entidad de dominio en la respuesta HTTP."""
    return ProductResponse(
        id=product.id,
        category_id=product.category_id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )
