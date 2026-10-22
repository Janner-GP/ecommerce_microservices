# catalog-service

Catálogo de productos de la tienda. Registra y consulta productos.

Sigue la misma estructura que `user-service`: Clean Architecture con dos adaptadores de persistencia que cumplen el mismo contrato.

```
HTTP → Router → Caso de uso → ProductRepository (contrato) ← Adaptador → PostgreSQL
```

- **Entidad:** `Product` en `domain/entities/` (clase normal, sin ORM)
- **Casos de uso:** CreateProduct, GetProduct
- **Adaptadores:** SQLModel y SQL directo con `psycopg`, en `infrastructure/repositories/`
- **Tablas:** `cat_categories`, `cat_products`

## Regla de negocio

El SKU no se puede repetir. Además de la validación del caso de uso, `sku` tiene restricción `UNIQUE` en la base, que protege contra dos peticiones simultáneas.

## Cambiar de SQLModel a SQL directo

En el `.env`:

```env
PERSISTENCE_ADAPTER=postgres   # o sqlmodel (por defecto)
```

Solo `presentation/dependencies.py` lee esa variable. El caso de uso, el contrato, el router y las migraciones no cambian. El commit y el rollback se hacen en `get_session` / `get_connection`, antes de enviar la respuesta (`scope="function"`).

## Uso

```bash
uv sync
cp .env.example .env          # completar DATABASE_URL
uv run alembic upgrade head
uv run fastapi dev app/src/main.py --port 8002
```

Endpoints:

- `POST /products` → 201, o 409 si el SKU ya existe
- `GET /products/{id}` → 200, o 404

Ejemplo de `POST /products`:

```json
{"sku": "CAM-001", "name": "Camiseta", "price": "45000.00", "stock": 10}
```

## Migraciones

Todos los microservicios comparten la base de datos. `alembic/env.py` solo revisa las tablas con prefijo `cat_` y guarda la versión en `cat_alembic_version`, así no interfiere con las migraciones de otros servicios.

## Pruebas

```bash
uv run pytest
```

Las pruebas del caso de uso no necesitan base de datos. Las de los dos adaptadores corren si defines `TEST_DATABASE_URL` (una base con las migraciones aplicadas) y hacen rollback al terminar.
