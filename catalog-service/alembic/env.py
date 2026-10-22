from logging.config import fileConfig
import os

from alembic import context
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

load_dotenv()

# Importar aquí los modelos que se quieren migrar
from app.src.domain.models.category import Category
from app.src.domain.models.product import Product

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

# Todos los microservicios usan la misma base de datos.
# Por eso cada uno:
#   - solo revisa las tablas que empiezan con su prefijo
#     (si no, el autogenerate propondría borrar las tablas de los demás);
#   - guarda su versión en su propia tabla de Alembic.
TABLE_PREFIX = "cat_"
VERSION_TABLE = "cat_alembic_version"

DATABASE_URL = os.getenv("DATABASE_URL", "").replace(
    "postgresql://", "postgresql+psycopg://"
)


def include_name(name, type_, parent_names):
    if type_ == "table":
        return name.startswith(TABLE_PREFIX)
    return True


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table=VERSION_TABLE,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=VERSION_TABLE,
            include_name=include_name,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
