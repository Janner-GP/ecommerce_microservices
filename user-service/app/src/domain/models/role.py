import uuid
from app.src.shared.utils.date import utc_now
from sqlmodel import Field, SQLModel

class Role(SQLModel, table=True):
    __tablename__ = "usr_roles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, max_length=80)
    description: str | None = None
