from sqlmodel import SQLModel, Field
import uuid

class UserRole(SQLModel, table=True):
    __tablename__ = "usr_user_roles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    role_id: uuid.UUID = Field(index=True)
