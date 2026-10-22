from sqlmodel import Session, create_engine

from app.src.shared.config import DATABASE_URL

# SQLAlchemy necesita saber que el driver es psycopg 3.
SQLMODEL_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

engine = create_engine(SQLMODEL_URL)


def get_session():
    """Abre una sesión por petición. Aquí, y solo aquí, se hace commit o rollback."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
