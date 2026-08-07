from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class LoginRequest(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TaskRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None

    class Config:
        orm_mode = True
