from sqlmodel import select

from app.src.domain.entities.product import Product
from app.src.domain.models.product import Product as ProductModel
from app.src.domain.repositories.product_repository import ProductRepository


class SQLModelProductRepository(ProductRepository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, product_id):
        model = self.session.get(ProductModel, product_id)

        if model is None:
            return None

        return to_domain(model)

    def get_by_sku(self, sku):
        statement = select(ProductModel).where(ProductModel.sku == sku)
        model = self.session.exec(statement).first()

        if model is None:
            return None

        return to_domain(model)

    def create(self, product):
        model = ProductModel(
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
        self.session.add(model)

        # flush envía el INSERT pero NO lo confirma: el commit lo hace get_session.
        self.session.flush()
        self.session.refresh(model)

        return to_domain(model)


def to_domain(model):
    """Convierte el modelo de SQLModel en la entidad de dominio."""
    return Product(
        id=model.id,
        category_id=model.category_id,
        sku=model.sku,
        name=model.name,
        description=model.description,
        price=model.price,
        stock=model.stock,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
