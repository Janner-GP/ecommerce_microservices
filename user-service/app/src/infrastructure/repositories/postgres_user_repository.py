from app.src.domain.entities.user import User, UserStatus
from app.src.domain.repositories.user_repository import UserRepository


class PostgresUserRepository(UserRepository):
    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, user_id):
        row = self.connection.execute(
            """
            SELECT id, name, identification_type, identification_number,
                   birthday_date, status, created_at, updated_at
            FROM usr_users
            WHERE id = %s
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            return None

        return to_domain(row)

    def get_by_identification(self, identification_number):
        # %s es un parámetro de psycopg, no formateo de texto:
        # el valor viaja separado de la consulta, así no hay inyección SQL.
        row = self.connection.execute(
            """
            SELECT id, name, identification_type, identification_number,
                   birthday_date, status, created_at, updated_at
            FROM usr_users
            WHERE identification_number = %s
            """,
            (identification_number,),
        ).fetchone()

        if row is None:
            return None

        return to_domain(row)

    def create(self, user):
        # El INSERT queda pendiente hasta que get_connection haga commit.
        row = self.connection.execute(
            """
            INSERT INTO usr_users (
                id, name, identification_type, identification_number,
                birthday_date, status, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, name, identification_type, identification_number,
                      birthday_date, status, created_at, updated_at
            """,
            (
                user.id,
                user.name,
                user.identification_type,
                user.identification_number,
                user.birthday_date,
                user.status.value,
                user.created_at,
                user.updated_at,
            ),
        ).fetchone()

        return to_domain(row)


def to_domain(row):
    """Convierte la fila cruda de PostgreSQL en la entidad de dominio."""
    return User(
        id=row[0],
        name=row[1],
        identification_type=row[2],
        identification_number=row[3],
        birthday_date=row[4],
        status=UserStatus(row[5]),
        created_at=row[6],
        updated_at=row[7],
    )
