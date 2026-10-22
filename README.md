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

## Guía para juniors: cómo crear un nuevo feature

Un feature nuevo se construye **de adentro hacia afuera**: primero el dominio, después el caso de uso, después la base de datos y al final HTTP. Así cada capa se escribe cuando ya existe aquello de lo que depende.

```
1. domain          → excepción, entidad y contrato (qué necesito)
2. application     → caso de uso (la regla de negocio)
3. tests           → prueba del caso de uso, sin base de datos
4. infrastructure  → los dos adaptadores (cómo se guarda)
5. presentation    → dependencia, esquema y endpoint (cómo se expone)
```

### Dónde va cada cosa

| Si necesitas… | Va en… |
|---|---|
| Una regla de negocio ("solo se cancela si está pendiente") | `application/use_cases/` |
| Un error de negocio | `domain/exceptions.py` |
| Una operación nueva con la base (buscar, actualizar…) | método en `domain/repositories/` + los dos adaptadores |
| Un campo o tabla nueva | `domain/entities/`, `domain/models/` y una migración |
| Una consulta SQL o de SQLModel | solo en `infrastructure/repositories/` |
| Validar el formato de la petición (tipos, longitudes) | `presentation/schemas/` |
| Convertir errores en códigos HTTP | `presentation/routers/` |

### Ejemplo completo: cancelar una orden

Vamos a agregar `PATCH /orders/{id}/cancel` en `order-service`. Regla: **solo se puede cancelar una orden en estado `PENDING`**.

#### Paso 0. ¿Cambia la base de datos?

Antes de escribir código, decide si el feature necesita columnas o tablas nuevas.

- **No** (como en este ejemplo: el campo `status` ya existe) → sigue al paso 1.
- **Sí** → agrega el campo en la entidad (`domain/entities/`) y en el modelo (`domain/models/`), y genera la migración:

```bash
uv run alembic revision --autogenerate -m "Agregar campo X a ord_orders"
# Revisa el archivo generado en alembic/versions/ antes de aplicarlo
uv run alembic upgrade head
```

Si creas una tabla nueva, su nombre debe empezar con el prefijo del servicio (`ord_`, `cat_`…) y el modelo debe importarse en `alembic/env.py`. Nunca edites una migración que ya se aplicó: crea una nueva.

#### Paso 1. La excepción de negocio

`domain/exceptions.py`

```python
class OrderCannotBeCancelledError(Exception):
    def __init__(self, order_id):
        super().__init__(f"La orden {order_id} ya no se puede cancelar")
```

#### Paso 2. El contrato del repositorio

Pregúntate: ¿qué necesita el caso de uso de la base de datos? Aquí, guardar el nuevo estado de una orden.

`domain/repositories/order_repository.py`

```python
    @abstractmethod
    def update_status(self, order: Order) -> Order: ...
```

> Al agregar un método al contrato, **todas** las clases que lo implementan deben tenerlo: los dos adaptadores y el repositorio en memoria de las pruebas. Si falta en alguno, Python lanza `TypeError: Can't instantiate abstract class`.

#### Paso 3. El caso de uso

`application/use_cases/cancel_order.py`

```python
from uuid import UUID

from app.src.domain.entities.order import Order, OrderStatus
from app.src.domain.exceptions import OrderCannotBeCancelledError, OrderNotFoundError
from app.src.domain.repositories.order_repository import OrderRepository
from app.src.shared.utils.date import utc_now


class CancelOrder:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_id: UUID) -> Order:
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        # Regla de negocio: solo se cancela una orden que aún no se ha pagado.
        if order.status != OrderStatus.PENDING:
            raise OrderCannotBeCancelledError(order_id)

        order.status = OrderStatus.CANCELLED
        order.updated_at = utc_now()

        return self.order_repository.update_status(order)
```

El caso de uso no sabe si detrás hay SQLModel o SQL directo: solo usa el contrato.

#### Paso 4. La prueba del caso de uso

En `tests/test_create_order.py`, agrega el método nuevo al repositorio en memoria:

```python
class InMemoryOrderRepository(OrderRepository):
    # ... métodos que ya existían ...

    def update_status(self, order):
        return order
```

Y en ese mismo archivo, las pruebas del feature:

```python
from app.src.application.use_cases.cancel_order import CancelOrder
from app.src.domain.exceptions import OrderCannotBeCancelledError


def new_order(status):
    item = OrderItem(product_id=uuid.uuid4(), quantity=1, unit_price=Decimal("1000"))
    return Order(user_id=uuid.uuid4(), items=[item], status=status)


def test_cancela_orden_pendiente():
    repository = InMemoryOrderRepository()
    order = repository.create(new_order(OrderStatus.PENDING))

    cancelled = CancelOrder(repository).execute(order.id)

    assert cancelled.status == OrderStatus.CANCELLED


def test_no_cancela_orden_pagada():
    repository = InMemoryOrderRepository()
    order = repository.create(new_order(OrderStatus.PAID))

    with pytest.raises(OrderCannotBeCancelledError):
        CancelOrder(repository).execute(order.id)
```

Corre `uv run pytest`. Si la regla está bien, estas pruebas pasan **sin tener base de datos**.

#### Paso 5. Adaptador SQLModel

`infrastructure/repositories/sqlmodel_order_repository.py`, dentro de la clase:

```python
    def update_status(self, order):
        order_model = self.session.get(OrderModel, order.id)
        order_model.status = order.status
        order_model.updated_at = order.updated_at
        self.session.add(order_model)

        # flush envía el UPDATE; el commit lo hace get_session.
        self.session.flush()

        return self.get_by_id(order.id)
```

#### Paso 6. Adaptador SQL directo

`infrastructure/repositories/postgres_order_repository.py`, dentro de la clase:

```python
    def update_status(self, order):
        # El UPDATE queda pendiente hasta que get_connection haga commit.
        self.connection.execute(
            """
            UPDATE ord_orders
            SET status = %s, updated_at = %s
            WHERE id = %s
            """,
            (order.status.value, order.updated_at, order.id),
        )

        return self.get_by_id(order.id)
```

Los dos adaptadores devuelven lo mismo: una entidad `Order`, nunca un modelo de SQLModel ni una fila cruda.

#### Paso 7. El esquema HTTP

Si el endpoint recibe un cuerpo nuevo o responde algo distinto, crea el esquema en `presentation/schemas/`. Aquí no hace falta: no hay cuerpo y la respuesta es el mismo `OrderResponse`.

#### Paso 8. La dependencia

`presentation/dependencies.py`

```python
from app.src.application.use_cases.cancel_order import CancelOrder


def get_cancel_order(order_repository=Depends(get_order_repository)):
    return CancelOrder(order_repository)
```

No elijas aquí un adaptador concreto: usa `get_order_repository`, que ya decide entre SQLModel y SQL directo.

#### Paso 9. El endpoint

`presentation/routers/order_router.py`

```python
@router.patch("/{order_id}/cancel")
def cancel_order(order_id: UUID, use_case=Depends(get_cancel_order)) -> OrderResponse:
    try:
        order = use_case.execute(order_id)
    except OrderNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except OrderCannotBeCancelledError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return to_response(order)
```

Recuerda importar `get_cancel_order` y `OrderCannotBeCancelledError` al inicio del archivo. El router solo traduce: recibe HTTP, llama al caso de uso y convierte los errores en códigos HTTP.

#### Paso 10. Verificar con los dos adaptadores

```bash
uv run pytest
```

Luego levanta el servicio y prueba el endpoint en `http://localhost:8003/docs`, primero con `PERSISTENCE_ADAPTER=sqlmodel` y después con `PERSISTENCE_ADAPTER=postgres`. Las respuestas deben ser iguales.

### Lista de revisión antes de subir el feature

- [ ] La regla de negocio está en el caso de uso, no en el router ni en el repositorio.
- [ ] El método nuevo del contrato está implementado en los dos adaptadores y en el repositorio en memoria.
- [ ] Los adaptadores devuelven entidades de dominio, no modelos ni filas.
- [ ] Las consultas SQL usan `%s` y una tupla de valores; nunca f-strings ni `+` con datos del usuario.
- [ ] Ningún repositorio hace `commit()`: eso lo hacen `get_session` y `get_connection`.
- [ ] Si cambió la base, hay una migración nueva y las tablas tienen el prefijo del servicio.
- [ ] `uv run pytest` pasa y el endpoint responde igual con los dos adaptadores.

### Errores comunes

| Error | Por qué está mal | Qué hacer |
|---|---|---|
| Escribir `select(...)` o SQL en el router | Mezcla HTTP con persistencia | Mover la consulta a un método del repositorio |
| Importar SQLModel en `domain/entities/` o en un caso de uso | La lógica queda atada al ORM | Usar la entidad de dominio |
| `f"... WHERE id = '{order_id}'"` | Abre la puerta a inyección SQL | `"... WHERE id = %s", (order_id,)` |
| Hacer `commit()` dentro del repositorio | Nadie sabe quién confirma la transacción | Dejar el commit en `get_session` / `get_connection` |
| Modificar una migración ya aplicada | La base y el código quedan desincronizados | Crear una migración nueva |
| Crear `get_postgres_...` en el router | El router queda atado a un adaptador | Usar solo las dependencias de `dependencies.py` |
