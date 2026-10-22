"""Contrato HTTP: no cambia aunque cambie el adaptador de persistencia."""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.src.domain.entities.user import UserStatus


class UserCreate(BaseModel):
    name: str = Field(max_length=150)
    identification_type: str = Field(max_length=30)
    identification_number: str = Field(max_length=50)
    birthday_date: date


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    identification_type: str
    identification_number: str
    birthday_date: date
    status: UserStatus
    created_at: datetime
    updated_at: datetime
