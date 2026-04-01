import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


# --- Auth ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Ideas ---
class IdeaCreate(BaseModel):
    title: str
    description: str


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class IdeaOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Messages ---
class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: uuid.UUID
    idea_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
