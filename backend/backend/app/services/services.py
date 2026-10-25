from sqlalchemy.orm import Session

from models.models import User
from models.models import Product
from models.models import Order
from models.models import Message, Project, Post, Customer, Category

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_products(db: Session) -> list[Product]:
    return db.query(Product).filter(Product.available == True).all()

def create_product(db: Session, name: str, description: str | None, price: float) -> Product:
    product = Product(name=name, description=description, price=price)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_orders(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).all()

def create_order(db: Session, user_id: int, total_amount: float) -> Order:
    order = Order(user_id=user_id, total_amount=total_amount)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def get_messages(db: Session) -> list[Message]:
    return db.query(Message).all()

def create_message(db: Session, name: str, description: str | None) -> Message:
    item = Message(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_projects(db: Session) -> list[Project]:
    return db.query(Project).all()

def create_project(db: Session, name: str, description: str | None) -> Project:
    item = Project(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_posts(db: Session) -> list[Post]:
    return db.query(Post).all()

def create_post(db: Session, name: str, description: str | None) -> Post:
    item = Post(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_customers(db: Session) -> list[Customer]:
    return db.query(Customer).all()

def create_customer(db: Session, name: str, description: str | None) -> Customer:
    item = Customer(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_categories(db: Session) -> list[Category]:
    return db.query(Category).all()

def create_category(db: Session, name: str, description: str | None) -> Category:
    item = Category(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
