from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from schemas.schemas import DoctorCreate, DoctorRead
from schemas.schemas import PatientCreate, PatientRead
from services.services import get_doctors, create_doctor, get_patients, create_patient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
router = APIRouter(prefix="/api")

@router.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}

@router.get('/doctors', response_model=list[DoctorRead])
def list_items(db: Session = Depends(get_db)): 
    return get_doctors(db)

@router.post('/doctors', response_model=DoctorRead)
def create_item(request: DoctorCreate, db: Session = Depends(get_db)): 
    return create_doctor(db, request.name, request.description)

@router.get('/patients', response_model=list[PatientRead])
def list_items(db: Session = Depends(get_db)): 
    return get_patients(db)

@router.post('/patients', response_model=PatientRead)
def create_item(request: PatientCreate, db: Session = Depends(get_db)): 
    return create_patient(db, request.name, request.description)
