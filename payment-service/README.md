# payment-service

Pagos de las órdenes. Registra y consulta pagos.

Sigue la misma estructura que `user-service`: Clean Architecture con dos adaptadores de persistencia que cumplen el mismo contrato.

```
HTTP → Router → Caso de uso → PaymentRepository (contrato) ← Adaptador → PostgreSQL
```

- **Entidad:** `Payment` en `domain/entities/` (clase normal, sin ORM)
- **Casos de uso:** CreatePayment, GetPayment
- **Adaptadores:** SQLModel y SQL directo con `psycopg`, en `infrastructure/repositories/`
- **Tablas:** `pym_payments`

## Regla de negocio

Una orden solo puede tener un pago. `order_id` además es `UNIQUE` en la base. Los pagos se crean en estado `PENDING`; métodos: `CARD`, `PSE`, `CASH`.

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
uv run fastapi dev app/src/main.py --port 8004
```

Endpoints:

- `POST /payments` → 201, o 409 si la orden ya tiene un pago
- `GET /payments/{id}` → 200, o 404

Ejemplo de `POST /payments`:

```json
{"order_id": "<uuid>", "amount": "100000.00", "method": "CARD"}
```

## Migraciones

Todos los microservicios comparten la base de datos. `alembic/env.py` solo revisa las tablas con prefijo `pym_` y guarda la versión en `pym_alembic_version`, así no interfiere con las migraciones de otros servicios.

## Pruebas

```bash
uv run pytest
```

Las pruebas del caso de uso no necesitan base de datos. Las de los dos adaptadores corren si defines `TEST_DATABASE_URL` (una base con las migraciones aplicadas) y hacen rollback al terminar.
