import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Adaptador de persistencia activo: "sqlmodel" o "postgres".
PERSISTENCE_ADAPTER = os.getenv("PERSISTENCE_ADAPTER", "sqlmodel")
