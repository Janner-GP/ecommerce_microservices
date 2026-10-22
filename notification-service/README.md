# notification-service

Notificaciones a los usuarios (correo y SMS). Las registra y las consulta.

Sigue la misma estructura que `user-service`: Clean Architecture con dos adaptadores de persistencia que cumplen el mismo contrato.

```
HTTP → Router → Caso de uso → NotificationRepository (contrato) ← Adaptador → PostgreSQL
```

- **Entidad:** `Notification` en `domain/entities/` (clase normal, sin ORM)
- **Casos de uso:** CreateNotification, GetNotification
- **Adaptadores:** SQLModel y SQL directo con `psycopg`, en `infrastructure/repositories/`
- **Tablas:** `ntf_notifications`

## Regla de negocio

Un correo (`EMAIL`) necesita un destinatario con `@` y un asunto; un `SMS` no necesita asunto. Se registran en estado `PENDING`: el envío real queda fuera de este ejemplo.

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
uv run fastapi dev app/src/main.py --port 8005
```

Endpoints:

- `POST /notifications` → 201, o 400 si un correo no tiene `@` o no tiene asunto
- `GET /notifications/{id}` → 200, o 404

Ejemplo de `POST /notifications`:

```json
{"user_id": "<uuid>", "channel": "EMAIL", "recipient": "ana@correo.com", "subject": "Pago", "message": "Pago recibido"}
```

## Migraciones

Todos los microservicios comparten la base de datos. `alembic/env.py` solo revisa las tablas con prefijo `ntf_` y guarda la versión en `ntf_alembic_version`, así no interfiere con las migraciones de otros servicios.

## Pruebas

```bash
uv run pytest
```

Las pruebas del caso de uso no necesitan base de datos. Las de los dos adaptadores corren si defines `TEST_DATABASE_URL` (una base con las migraciones aplicadas) y hacen rollback al terminar.
