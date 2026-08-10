from sqlalchemy.orm import Session

from models.models import Doctor
from models.models import Patient

def get_doctors(db: Session, created_by_id: int | None = None) -> list[Doctor]:
    query = db.query(Doctor)
    if created_by_id is not None:
        query = query.filter(Doctor.created_by_id == created_by_id)
    return query.all()

def create_doctor(db: Session, name: str, description: str | None = None, created_by_id: int | None = None) -> Doctor:
    item = Doctor(name=name, description=description, created_by_id=created_by_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_patients(db: Session, created_by_id: int | None = None) -> list[Patient]:
    query = db.query(Patient)
    if created_by_id is not None:
        query = query.filter(Patient.created_by_id == created_by_id)
    return query.all()

def create_patient(db: Session, name: str, description: str | None = None, created_by_id: int | None = None) -> Patient:
    item = Patient(name=name, description=description, created_by_id=created_by_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
