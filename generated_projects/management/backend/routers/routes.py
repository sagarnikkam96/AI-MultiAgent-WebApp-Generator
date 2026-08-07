from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from fastapi.security import OAuth2PasswordBearer
from auth.jwt import create_access_token, hash_password, verify_access_token, verify_password
from models.models import User
from schemas.schemas import LoginRequest, Token, UserCreate, UserRead
from schemas.schemas import TaskCreate, TaskRead
from services.services import get_user_by_email, create_user, get_tasks, create_task

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
router = APIRouter(prefix="/api")

@router.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = verify_access_token(token)
    email = payload.get('sub')
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication token')
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid user credentials')
    return user

@router.post('/login', response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)): 
    user = get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    access_token = create_access_token(user.email)
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.post('/register', response_model=UserRead)
def register(request: UserCreate, db: Session = Depends(get_db)): 
    existing = get_user_by_email(db, request.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    user = create_user(db, request.email, hash_password(request.password))
    return user

@router.get('/tasks', response_model=list[TaskRead])
def list_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)): 
    return get_tasks(db, created_by_id=current_user.id)

@router.post('/tasks', response_model=TaskRead)
def create_item(request: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)): 
    return create_task(db, request.name, request.description, created_by_id=current_user.id)
