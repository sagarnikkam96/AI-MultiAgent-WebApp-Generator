from sqlalchemy.orm import Session

from models.models import Project

def get_projects(db: Session, created_by_id: int | None = None) -> list[Project]:
    query = db.query(Project)
    if created_by_id is not None:
        query = query.filter(Project.created_by_id == created_by_id)
    return query.all()

def create_project(db: Session, name: str, description: str | None = None, created_by_id: int | None = None) -> Project:
    item = Project(name=name, description=description, created_by_id=created_by_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
