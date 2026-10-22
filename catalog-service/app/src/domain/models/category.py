import uuid

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "cat_categories"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, max_length=80)
    description: str | None = None
