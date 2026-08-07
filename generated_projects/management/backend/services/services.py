from sqlalchemy.orm import Session

from models.models import User
from models.models import Task

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_tasks(db: Session, created_by_id: int | None = None) -> list[Task]:
    query = db.query(Task)
    if created_by_id is not None:
        query = query.filter(Task.created_by_id == created_by_id)
    return query.all()

def create_task(db: Session, name: str, description: str | None = None, created_by_id: int | None = None) -> Task:
    item = Task(name=name, description=description, created_by_id=created_by_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
