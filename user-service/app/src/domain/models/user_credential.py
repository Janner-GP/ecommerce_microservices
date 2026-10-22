from datetime import datetime
import uuid
from app.src.shared.utils.date import utc_now
from sqlmodel import Field, SQLModel


class UserCredential(SQLModel, table=True):
    __tablename__ = "usr_user_credentials"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True, unique=True)
    password_hash: str = Field(max_length=255)

    created_at: datetime = Field(default_factory=utc_now)
    password_changed_at: datetime | None = None
