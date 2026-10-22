# ecommerce_microservices

Ecommerce dividido en cinco microservicios con FastAPI, SQLModel, PostgreSQL y Alembic. Todos siguen Clean Architecture y tienen dos adaptadores de persistencia que cumplen el mismo contrato:

- **SQLModel** (ORM)
- **SQL directo** con `psycopg`

Cambiar de uno a otro no obliga a reescribir los casos de uso, los contratos ni la API: se elige con `PERSISTENCE_ADAPTER` en el `.env` de cada servicio.

```
HTTP → Router → Caso de uso → Contrato de repositorio ← Adaptador → PostgreSQL
```

## Microservicios

| Servicio | Puerto | Prefijo de tablas | Qué hace |
|---|---|---|---|
| [user-service](user-service) | 8001 | `usr_` | Registra y consulta usuarios |
| [catalog-service](catalog-service) | 8002 | `cat_` | Registra y consulta productos |
| [order-service](order-service) | 8003 | `ord_` | Crea órdenes con sus ítems y las consulta |
| [payment-service](payment-service) | 8004 | `pym_` | Registra el pago de una orden y lo consulta |
| [notification-service](notification-service) | 8005 | `ntf_` | Registra notificaciones por correo o SMS |

Cada servicio es un proyecto independiente con su propio `pyproject.toml`, migraciones, pruebas y README.

## Estructura de cada servicio

```
app/src/
├── domain/
│   ├── entities/        # Entidades de dominio (clases normales, sin ORM)
│   ├── models/          # Tablas SQLModel (las usa Alembic)
│   ├── repositories/    # Contrato del repositorio
│   └── exceptions.py
├── application/use_cases/
├── infrastructure/
│   ├── database/        # get_session (SQLModel) y get_connection (psycopg)
│   └── repositories/    # Adaptador SQLModel y adaptador SQL directo
├── presentation/
│   ├── dependencies.py  # Punto de composición: elige el adaptador
│   ├── schemas/         # Contrato HTTP
│   └── routers/
└── main.py
```

## Base de datos compartida

Los cinco servicios pueden usar la misma base de PostgreSQL. Para que no se pisen:

- cada servicio crea solo tablas con su prefijo (`usr_`, `cat_`, `ord_`, `pym_`, `ntf_`);
- `alembic/env.py` solo compara las tablas de su prefijo, así el autogenerate no propone borrar las de otros servicios;
- cada servicio guarda su versión de Alembic en su propia tabla (`cat_alembic_version`, `ord_alembic_version`…). `user-service` conserva `alembic_version`.

Entre servicios no hay foreign keys: una orden guarda el `user_id` y el `product_id` como identificadores, porque esos datos pertenecen a otros servicios.

## Uso

Dentro de cada servicio:

```bash
uv sync
cp .env.example .env          # completar DATABASE_URL
uv run alembic upgrade head
uv run fastapi dev app/src/main.py --port 8001
```

## Pruebas

```bash
uv run pytest
```

Las pruebas de los casos de uso no necesitan base de datos. Las de los adaptadores ejecutan la misma prueba con SQLModel y con SQL directo si se define `TEST_DATABASE_URL`.
