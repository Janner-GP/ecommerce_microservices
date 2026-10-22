# user-service

Microservicio de usuarios de la plataforma de reservas. Registra y consulta usuarios con FastAPI y PostgreSQL, siguiendo Clean Architecture.

La persistencia se puede hacer de dos formas sin tocar la lógica de negocio:

- **SQLModel** (ORM) → `SQLModelUserRepository`
- **SQL directo** con `psycopg` → `PostgresUserRepository`

```
HTTP → Router → Caso de uso → UserRepository (contrato) ← Adaptador → PostgreSQL
```

## Estructura

```
app/src/
├── domain/
│   ├── entities/user.py              # Entidad User (clase normal, sin ORM)
│   ├── repositories/user_repository.py  # Contrato UserRepository
│   ├── exceptions.py                 # UserAlreadyExistsError, UserNotFoundError
│   └── models/                       # Tablas SQLModel (las usa Alembic)
├── application/use_cases/            # CreateUser, GetUser
├── infrastructure/
│   ├── database/                     # get_session (SQLModel) y get_connection (psycopg)
│   └── repositories/                 # Los dos adaptadores
├── presentation/
│   ├── dependencies.py               # Punto de composición: elige el adaptador
│   ├── schemas/user_schemas.py       # Contrato HTTP
│   └── routers/user_router.py
└── main.py
```

## Cambiar de SQLModel a SQL directo

En el `.env`:

```env
PERSISTENCE_ADAPTER=postgres   # o sqlmodel (por defecto)
```

`presentation/dependencies.py` es el único lugar que lee esa variable. El router, los casos de uso, el contrato, las migraciones y la API no cambian.

| Componente | ¿Cambia al cambiar de adaptador? |
|---|---|
| `CreateUser`, `GetUser` | No |
| `UserRepository` | No |
| Router y esquemas HTTP | No |
| Adaptador de persistencia | Sí |
| Sesión (SQLModel) / conexión (psycopg) | Sí |
| Conversión fila/modelo → `User` | Sí, cada adaptador tiene su `_to_domain` |
| Migraciones | No: ambos usan la tabla `usr_users` |

### Transacciones

El commit y el rollback se hacen en un único sitio por adaptador, al final de cada petición:

- `infrastructure/database/sqlmodel_session.py` → `get_session`
- `infrastructure/database/postgres_connection.py` → `get_connection`

Los repositorios nunca hacen commit (SQLModel usa `flush()`, que envía el `INSERT` sin confirmarlo).

En `dependencies.py` se usa `Depends(get_session, scope="function")`. Sin `scope="function"`, FastAPI envía la respuesta antes de ejecutar el código que va después del `yield`: si el commit fallara, el cliente ya habría recibido un 201. Con `scope="function"` se confirma primero y después se responde.

Se usa la forma `param=Depends(...)` en lugar de `Annotated[...]` para que el código sea más fácil de leer en clase. FastAPI recomienda `Annotated`, pero las dos formas funcionan igual.

### Entidad vs. modelo de tabla

`domain/entities/user.py` es lo que usa el caso de uso y no depende de SQLModel. `domain/models/user.py` es la tabla que necesita Alembic. Se mantienen separadas para que el adaptador SQL no necesite SQLModel. `UserStatus` se define una sola vez, en la entidad.

## Uso

```bash
uv sync
cp .env.example .env          # completar DATABASE_URL
uv run alembic upgrade head
uv run fastapi dev app/src/main.py --port 8001
```

Endpoints:

- `POST /users` → 201, o 409 si la identificación ya existe
- `GET /users/{id}` → 200, o 404

## Pruebas

```bash
uv run pytest
```

- `tests/test_create_user.py`: prueba el caso de uso con un repositorio en memoria, sin base de datos.
- `tests/test_user_repositories.py`: ejecuta la misma prueba contra los dos adaptadores. Solo corre si defines `TEST_DATABASE_URL` (una base con las migraciones aplicadas). Hace rollback y no deja datos.

```bash
TEST_DATABASE_URL=postgresql://postgres:test@localhost:5432/postgres uv run pytest
```

## Migraciones

Todos los microservicios comparten la base de datos. `alembic/env.py` solo revisa las tablas con prefijo `usr_`, así el autogenerate no intenta borrar las tablas de otros servicios. Este servicio guarda su versión en `alembic_version` (la tabla por defecto) porque su primera migración ya pudo aplicarse con ese nombre; los demás usan su propia tabla (`cat_alembic_version`, `ord_alembic_version`…).

## Pendientes conocidos

- `identification_number` no tiene restricción `UNIQUE` en la base. La validación del caso de uso no evita que dos peticiones simultáneas registren la misma identificación; para eso hace falta una migración que añada la restricción.
