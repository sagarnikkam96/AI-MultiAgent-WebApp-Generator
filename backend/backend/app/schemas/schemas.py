from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class LoginRequest(BaseModel):
    email: str
    password: str

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ProductRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    available: bool

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    user_id: int
    total_amount: float

class OrderRead(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float

    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = 'General'
    status: Optional[str] = 'Active'

class MessageRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    status: str

    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = 'General'
    status: Optional[str] = 'Active'

class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    status: str

    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = 'General'
    status: Optional[str] = 'Active'

class PostRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    status: str

    class Config:
        orm_mode = True

class CustomerCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = 'General'
    status: Optional[str] = 'Active'

class CustomerRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    status: str

    class Config:
        orm_mode = True

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = 'General'
    status: Optional[str] = 'Active'

class CategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    status: str

    class Config:
        orm_mode = True
