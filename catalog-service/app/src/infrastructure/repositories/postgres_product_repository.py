from app.src.domain.entities.product import Product
from app.src.domain.repositories.product_repository import ProductRepository


class PostgresProductRepository(ProductRepository):
    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, product_id):
        row = self.connection.execute(
            """
            SELECT id, category_id, sku, name, description,
                   price, stock, is_active, created_at, updated_at
            FROM cat_products
            WHERE id = %s
            """,
            (product_id,),
        ).fetchone()

        if row is None:
            return None

        return to_domain(row)

    def get_by_sku(self, sku):
        # %s es un parámetro de psycopg, no formateo de texto:
        # el valor viaja separado de la consulta, así no hay inyección SQL.
        row = self.connection.execute(
            """
            SELECT id, category_id, sku, name, description,
                   price, stock, is_active, created_at, updated_at
            FROM cat_products
            WHERE sku = %s
            """,
            (sku,),
        ).fetchone()

        if row is None:
            return None

        return to_domain(row)

    def create(self, product):
        # El INSERT queda pendiente hasta que get_connection haga commit.
        row = self.connection.execute(
            """
            INSERT INTO cat_products (
                id, category_id, sku, name, description,
                price, stock, is_active, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, category_id, sku, name, description,
                      price, stock, is_active, created_at, updated_at
            """,
            (
                product.id,
                product.category_id,
                product.sku,
                product.name,
                product.description,
                product.price,
                product.stock,
                product.is_active,
                product.created_at,
                product.updated_at,
            ),
        ).fetchone()

        return to_domain(row)


def to_domain(row):
    """Convierte la fila cruda de PostgreSQL en la entidad de dominio."""
    return Product(
        id=row[0],
        category_id=row[1],
        sku=row[2],
        name=row[3],
        description=row[4],
        price=row[5],
        stock=row[6],
        is_active=row[7],
        created_at=row[8],
        updated_at=row[9],
    )
