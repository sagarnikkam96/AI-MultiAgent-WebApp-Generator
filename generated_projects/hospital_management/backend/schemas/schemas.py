from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DoctorCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DoctorRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PatientCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PatientRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
