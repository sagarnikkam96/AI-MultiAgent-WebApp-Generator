from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from schemas.schemas import ProjectCreate, ProjectRead
from services.services import get_projects, create_project

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
router = APIRouter()

@router.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}

@router.get('/projects', response_model=list[ProjectRead])
def list_items(db: Session = Depends(get_db)): 
    return get_projects(db)

@router.post('/projects', response_model=ProjectRead)
def create_item(request: ProjectCreate, db: Session = Depends(get_db)): 
    return create_project(db, request.name, request.description)
