from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.connection import get_db
from models.models import User, Product, Message, Project, Post, Order, Customer, Category
from auth.jwt import create_access_token
from schemas.schemas import LoginRequest, Token, UserCreate, UserRead
from schemas.schemas import ProductCreate, ProductRead
from schemas.schemas import OrderCreate, OrderRead
from schemas.schemas import MessageCreate, MessageRead
from schemas.schemas import ProjectCreate, ProjectRead
from schemas.schemas import PostCreate, PostRead
from schemas.schemas import CustomerCreate, CustomerRead
from schemas.schemas import CategoryCreate, CategoryRead
from services.services import get_user_by_email, create_user, get_products, create_product, get_orders, create_order

router = APIRouter()

@router.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    email = token.split(':', 1)[0]
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication token')
    return user

@router.get('/counts')
def database_counts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, int]:
    counts = {
        'products': db.query(Product).filter(Product.created_by_id == current_user.id).count(),
        'messages': db.query(Message).filter(Message.created_by_id == current_user.id).count(),
        'projects': db.query(Project).filter(Project.created_by_id == current_user.id).count(),
        'posts': db.query(Post).filter(Post.created_by_id == current_user.id).count(),
        'orders': db.query(Order).filter(Order.created_by_id == current_user.id).count(),
        'customers': db.query(Customer).filter(Customer.created_by_id == current_user.id).count(),
        'categories': db.query(Category).filter(Category.created_by_id == current_user.id).count(),
    }
    counts['total'] = sum(counts.values())
    return counts

@router.post('/login', response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)): 
    user = get_user_by_email(db, request.email)
    if not user or user.hashed_password != request.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    access_token = create_access_token(request.email)
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.post('/register', response_model=UserRead)
def register(request: UserCreate, db: Session = Depends(get_db)): 
    existing = get_user_by_email(db, request.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    user = create_user(db, request.email, request.password)
    return user

@router.get('/products', response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)): 
    return get_products(db)

@router.get('/orders', response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)): 
    return get_orders(db, user_id=1)

@router.get('/messages', response_model=list[MessageRead])
def list_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Message)
    query = query.filter(Message.created_by_id == current_user.id)
    return query.order_by(Message.created_at.desc()).all()

@router.post('/messages', response_model=MessageRead)
def create_message(request: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = Message(name=request.name, description=request.description, category=request.category or 'General', status=request.status or 'Active', created_by_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get('/projects', response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Project)
    query = query.filter(Project.created_by_id == current_user.id)
    return query.order_by(Project.created_at.desc()).all()

@router.post('/projects', response_model=ProjectRead)
def create_project(request: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = Project(name=request.name, description=request.description, category=request.category or 'General', status=request.status or 'Active', created_by_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get('/posts', response_model=list[PostRead])
def list_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Post)
    query = query.filter(Post.created_by_id == current_user.id)
    return query.order_by(Post.created_at.desc()).all()

@router.post('/posts', response_model=PostRead)
def create_post(request: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = Post(name=request.name, description=request.description, category=request.category or 'General', status=request.status or 'Active', created_by_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get('/customers', response_model=list[CustomerRead])
def list_customers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Customer)
    query = query.filter(Customer.created_by_id == current_user.id)
    return query.order_by(Customer.created_at.desc()).all()

@router.post('/customers', response_model=CustomerRead)
def create_customer(request: CustomerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = Customer(name=request.name, description=request.description, category=request.category or 'General', status=request.status or 'Active', created_by_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get('/categories', response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Category)
    query = query.filter(Category.created_by_id == current_user.id)
    return query.order_by(Category.created_at.desc()).all()

@router.post('/categories', response_model=CategoryRead)
def create_category(request: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = Category(name=request.name, description=request.description, category=request.category or 'General', status=request.status or 'Active', created_by_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
