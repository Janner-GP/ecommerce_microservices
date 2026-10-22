import psycopg

from app.src.shared.config import DATABASE_URL

# psycopg no entiende el prefijo "+psycopg" que usa SQLAlchemy.
POSTGRES_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


def get_connection():
    """Abre una conexión por petición. Aquí, y solo aquí, se hace commit o rollback."""
    connection = psycopg.connect(POSTGRES_URL)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
