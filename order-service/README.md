# order-service

Órdenes de compra. Crea una orden con sus productos y la consulta.

Sigue la misma estructura que `user-service`: Clean Architecture con dos adaptadores de persistencia que cumplen el mismo contrato.

```
HTTP → Router → Caso de uso → OrderRepository (contrato) ← Adaptador → PostgreSQL
```

- **Entidad:** `Order, OrderItem` en `domain/entities/` (clase normal, sin ORM)
- **Casos de uso:** CreateOrder, GetOrder
- **Adaptadores:** SQLModel y SQL directo con `psycopg`, en `infrastructure/repositories/`
- **Tablas:** `ord_orders`, `ord_order_items`

## Regla de negocio

La orden necesita al menos un ítem con cantidad mayor que 0, y el total lo calcula el caso de uso. La orden y sus ítems se guardan en la misma transacción: si un ítem falla, el rollback deshace todo.

`user_id` y `product_id` son solo identificadores: el usuario vive en user-service y el producto en catalog-service, por eso no hay foreign key hacia ellos. En este ejemplo el precio unitario llega en la petición; en un sistema real se consultaría a catalog-service.

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
uv run fastapi dev app/src/main.py --port 8003
```

Endpoints:

- `POST /orders` → 201, o 400 si no tiene ítems o alguna cantidad es 0
- `GET /orders/{id}` → 200, o 404

Ejemplo de `POST /orders`:

```json
{"user_id": "<uuid>", "items": [{"product_id": "<uuid>", "quantity": 2, "unit_price": "45000.00"}]}
```

## Migraciones

Todos los microservicios comparten la base de datos. `alembic/env.py` solo revisa las tablas con prefijo `ord_` y guarda la versión en `ord_alembic_version`, así no interfiere con las migraciones de otros servicios.

## Pruebas

```bash
uv run pytest
```

Las pruebas del caso de uso no necesitan base de datos. Las de los dos adaptadores corren si defines `TEST_DATABASE_URL` (una base con las migraciones aplicadas) y hacen rollback al terminar.
