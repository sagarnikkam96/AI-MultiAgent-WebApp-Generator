from __future__ import annotations

import ast
import re
from typing import Any, Protocol

from .code_generator import CodeGenerator, PromptProvider
from .code_schema import GeneratedFile
from .project_slug import project_slug
from .website_spec import derive_website_spec


class BackendGenerator(CodeGenerator):
    """Generates backend code artifacts for Version 2."""

    def generate_files(
        self,
        prompt_provider: PromptProvider,
        project_name: str = "",
        requirements: Any = None,
        language: str = "en",
    ) -> list[GeneratedFile]:
        """Create backend files from the given prompt provider."""
        raw_prompt = getattr(prompt_provider, "prompt", None)
        prompt = raw_prompt.strip() if isinstance(raw_prompt, str) and raw_prompt.strip() else prompt_provider.get_prompt()
        generated_files = self._build_backend_files(prompt)
        slug = project_slug(project_name.strip() or prompt)
        project_root = f"generated_projects/{slug}"
        generated_files = [
            GeneratedFile(path=f"{project_root}/{generated_file.path}", content=generated_file.content)
            for generated_file in generated_files
        ]
        self._validate_generated_files(generated_files)
        return generated_files

    def _build_backend_files(self, prompt: str) -> list[GeneratedFile]:
        """Construct the backend file list based on natural language requirements."""
        requirements = prompt.strip()
        has_postgres = self._requires_postgres(requirements)
        has_auth = self._requires_auth(requirements)
        entities = self._extract_entities(requirements)
        website_spec = derive_website_spec(requirements)
        if website_spec.get("key") == "generic":
            module_labels = website_spec.get("module_labels", {})
        else:
            module_labels = {module: module for module in website_spec.get("components", [])}
        special_entities = {
            "Cart": "CartItem", "Menu": "MenuItem", "Categories": "Category",
            "Companies": "Company", "Policies": "Policy", "Faculty": "Faculty",
        }
        for component, label in module_labels.items():
            words = re.findall(r"[A-Za-z0-9]+", label)
            if not words:
                continue
            entity = special_entities.get(component)
            if entity is None:
                entity = "".join(word.title() for word in words)
                if entity.endswith("ies"):
                    entity = f"{entity[:-3]}y"
                elif entity.endswith("s") and not entity.endswith(("ss", "us", "is")):
                    entity = entity[:-1]
            if entity not in entities:
                entities.append(entity)

        if has_auth and "User" not in entities:
            entities.insert(0, "User")

        requires_database = has_postgres or bool(entities)

        generated_files: list[GeneratedFile] = []

        generated_files.append(
            GeneratedFile(
                path="backend/app/__init__.py",
                content=self._package_init_content(),
            )
        )
        generated_files.append(
            GeneratedFile(
                path="backend/requirements.txt",
                content=self._requirements_content(has_postgres),
            )
        )
        generated_files.append(
            GeneratedFile(
                path="backend/README.md",
                content=(
                    "# Generated backend\n\n"
                    "From this directory, install dependencies and start the API:\n\n"
                    "1. `python -m pip install -r requirements.txt`\n"
                    "2. `python -m uvicorn app.main:app --reload --port 8001`\n\n"
                    "The generated frontend reads database counts from this API. "
                    "Its default API address is `http://127.0.0.1:8001`; set "
                    "`VITE_API_BASE_URL` before building the frontend if you use a different host or port.\n"
                ),
            )
        )

        if requires_database:
            generated_files.append(
                GeneratedFile(
                    path="backend/app/database/connection.py",
                    content=self._database_connection_content(has_postgres),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path="backend/app/database/__init__.py",
                    content=self._package_init_content(),
                )
            )

            generated_files.append(
                GeneratedFile(
                    path="backend/app/models/models.py",
                    content=self._models_content(entities, has_auth),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path="backend/app/models/__init__.py",
                    content=self._package_init_content(),
                )
            )

        generated_files.append(
            GeneratedFile(
                path="backend/app/schemas/schemas.py",
                content=self._schemas_content(entities, has_auth),
            )
        )
        generated_files.append(
            GeneratedFile(
                path="backend/app/schemas/__init__.py",
                content=self._package_init_content(),
            )
        )

        if requires_database:
            generated_files.append(
                GeneratedFile(
                    path="backend/app/services/services.py",
                    content=self._services_content(entities, has_auth),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path="backend/app/services/__init__.py",
                    content=self._package_init_content(),
                )
            )

        generated_files.append(
            GeneratedFile(
                path="backend/app/routers/routes.py",
                content=self._routers_content(entities, has_auth, requires_database),
            )
        )
        generated_files.append(
            GeneratedFile(
                path="backend/app/routers/__init__.py",
                content=self._package_init_content(),
            )
        )

        if has_auth:
            generated_files.append(
                GeneratedFile(
                    path="backend/app/auth/jwt.py",
                    content=self._auth_jwt_content(),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path="backend/app/auth/__init__.py",
                    content=self._package_init_content(),
                )
            )

        generated_files.append(
            GeneratedFile(
                path="backend/app/main.py",
                content=self._main_content(has_auth, requires_database),
            )
        )

        return generated_files

    def _requires_postgres(self, requirements: str) -> bool:
        text = requirements.lower()
        return "postgres" in text or "postgresql" in text

    def _requires_auth(self, requirements: str) -> bool:
        text = requirements.lower()
        return any(keyword in text for keyword in ["login", "signup", "register", "authentication", "auth", "jwt", "token"])

    def _extract_entities(self, requirements: str) -> list[str]:
        text = requirements.lower()
        entity_map = {
            "task": "Task",
            "tasks": "Task",
            "todo": "Todo",
            "todos": "Todo",
            "product": "Product",
            "products": "Product",
            "order": "Order",
            "orders": "Order",
            "cart": "CartItem",
            "user": "User",
            "users": "User",
            "customer": "Customer",
            "customers": "Customer",
            "ticket": "Ticket",
            "tickets": "Ticket",
            "message": "Message",
            "messages": "Message",
            "event": "Event",
            "events": "Event",
            "project": "Project",
            "projects": "Project",
            "post": "Post",
            "posts": "Post",
            "comment": "Comment",
            "comments": "Comment",
            "note": "Note",
            "notes": "Note",
        }

        entities: list[str] = []
        for keyword, entity_name in entity_map.items():
            if re.search(rf"\b{re.escape(keyword)}\b", text) and entity_name not in entities:
                entities.append(entity_name)

        return entities

    def _database_connection_content(self, use_postgres: bool) -> str:
        if use_postgres:
            return (
                "from sqlalchemy import create_engine\n"
                "from sqlalchemy.orm import sessionmaker\n"
                "\n"
                "DATABASE_URL = 'postgresql://user:password@localhost:5432/app_db'\n"
                "engine = create_engine(DATABASE_URL, future=True)\n"
                "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
                "\n"
                "def get_db():\n"
                "    db = SessionLocal()\n"
                "    try:\n"
                "        yield db\n"
                "    finally:\n"
                "        db.close()\n"
            )

        return (
            "from sqlalchemy import create_engine\n"
            "from sqlalchemy.orm import sessionmaker\n"
            "\n"
            "DATABASE_URL = 'sqlite:///./app.db'\n"
            "engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})\n"
            "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
            "\n"
            "def get_db():\n"
            "    db = SessionLocal()\n"
            "    try:\n"
            "        yield db\n"
            "    finally:\n"
            "        db.close()\n"
        )

    def _models_content(self, entities: list[str], has_auth: bool) -> str:
        has_user = "User" in entities
        lines = [
            "from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean, Float\n",
            "from sqlalchemy.orm import declarative_base, relationship\n",
            "from datetime import datetime\n",
            "\n",
            "Base = declarative_base()\n",
            "\n",
        ]

        if has_user:
            lines.extend(
                [
                    "class User(Base):\n",
                    "    __tablename__ = 'users'\n",
                    "    id = Column(Integer, primary_key=True, index=True)\n",
                    "    email = Column(String, unique=True, index=True, nullable=False)\n",
                    "    hashed_password = Column(String, nullable=False)\n",
                    "    is_active = Column(Boolean, default=True, nullable=False)\n",
                    "    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)\n",
                    "\n",
                ]
            )

        if "Task" in entities:
            lines.extend(
                [
                    "class Task(Base):\n",
                    "    __tablename__ = 'tasks'\n",
                    "    id = Column(Integer, primary_key=True, index=True)\n",
                    "    title = Column(String, nullable=False)\n",
                    "    description = Column(Text, nullable=True)\n",
                    "    completed = Column(Boolean, default=False, nullable=False)\n",
                    "    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)\n",
                    "    owner = relationship('User', back_populates='tasks')\n",
                    "\n",
                ]
            )

        if "Product" in entities:
            lines.extend(
                [
                    "class Product(Base):\n",
                    "    __tablename__ = 'products'\n",
                    "    id = Column(Integer, primary_key=True, index=True)\n",
                    "    name = Column(String, nullable=False)\n",
                    "    description = Column(Text, nullable=True)\n",
                    "    price = Column(Float, nullable=False, default=0.0)\n",
                    "    available = Column(Boolean, default=True, nullable=False)\n",
                    "\n",
                ]
            )

        if "Order" in entities:
            lines.extend(
                [
                    "class Order(Base):\n",
                    "    __tablename__ = 'orders'\n",
                    "    id = Column(Integer, primary_key=True, index=True)\n",
                    "    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)\n",
                    "    status = Column(String, default='pending', nullable=False)\n",
                    "    total_amount = Column(Float, nullable=False, default=0.0)\n",
                    "    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)\n",
                    "    user = relationship('User')\n",
                    "\n",
                ]
            )

        if "CartItem" in entities:
            lines.extend(
                [
                    "class CartItem(Base):\n",
                    "    __tablename__ = 'cart_items'\n",
                    "    id = Column(Integer, primary_key=True, index=True)\n",
                    "    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)\n",
                    "    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)\n",
                    "    quantity = Column(Integer, nullable=False, default=1)\n",
                    "    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)\n",
                    "\n",
                ]
            )

        if "Todo" in entities:
            lines.extend(
                [
                    "class Todo(Base):\n",
                    "    __tablename__ = 'todos'\n",
                    "    id = Column(Integer, primary_key=True, index=True)\n",
                    "    title = Column(String, nullable=False)\n",
                    "    completed = Column(Boolean, default=False, nullable=False)\n",
                    "    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)\n",
                    "    owner = relationship('User')\n",
                    "\n",
                ]
            )

        handled_entities = {"User", "Task", "Product", "Order", "CartItem", "Todo"}
        for entity in entities:
            if entity in handled_entities:
                continue
            table_name = self._plural_name(self._snake_case(entity))
            lines.extend([
                f"class {entity}(Base):\n",
                f"    __tablename__ = {table_name!r}\n",
                "    id = Column(Integer, primary_key=True, index=True)\n",
                "    name = Column(String, nullable=False)\n",
                "    description = Column(Text, nullable=True)\n",
                "    category = Column(String, nullable=False, default='General')\n",
                "    status = Column(String, nullable=False, default='Active')\n",
                "    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)\n",
            ])
            if has_auth:
                lines.append("    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)\n")
            lines.append("\n")

        return "".join(lines)

    def _schemas_content(self, entities: list[str], has_auth: bool) -> str:
        lines = [
            "from pydantic import BaseModel\n",
            "from typing import Optional\n",
            "\n",
        ]

        if has_auth:
            lines.extend(
                [
                    "class UserCreate(BaseModel):\n",
                    "    email: str\n",
                    "    password: str\n",
                    "\n",
                    "class UserRead(BaseModel):\n",
                    "    id: int\n",
                    "    email: str\n",
                    "    is_active: bool\n",
                    "\n",
                    "    class Config:\n",
                    "        orm_mode = True\n",
                    "\n",
                    "class Token(BaseModel):\n",
                    "    access_token: str\n",
                    "    token_type: str = 'bearer'\n",
                    "\n",
                    "class LoginRequest(BaseModel):\n",
                    "    email: str\n",
                    "    password: str\n",
                    "\n",
                ]
            )

        if "Task" in entities:
            lines.extend(
                [
                    "class TaskCreate(BaseModel):\n",
                    "    title: str\n",
                    "    description: Optional[str] = None\n",
                    "\n",
                    "class TaskRead(BaseModel):\n",
                    "    id: int\n",
                    "    title: str\n",
                    "    description: Optional[str] = None\n",
                    "    completed: bool\n",
                    "\n",
                    "    class Config:\n",
                    "        orm_mode = True\n",
                    "\n",
                ]
            )

        if "Product" in entities:
            lines.extend(
                [
                    "class ProductCreate(BaseModel):\n",
                    "    name: str\n",
                    "    description: Optional[str] = None\n",
                    "    price: float\n",
                    "\n",
                    "class ProductRead(BaseModel):\n",
                    "    id: int\n",
                    "    name: str\n",
                    "    description: Optional[str] = None\n",
                    "    price: float\n",
                    "    available: bool\n",
                    "\n",
                    "    class Config:\n",
                    "        orm_mode = True\n",
                    "\n",
                ]
            )

        if "Order" in entities:
            lines.extend(
                [
                    "class OrderCreate(BaseModel):\n",
                    "    user_id: int\n",
                    "    total_amount: float\n",
                    "\n",
                    "class OrderRead(BaseModel):\n",
                    "    id: int\n",
                    "    user_id: int\n",
                    "    status: str\n",
                    "    total_amount: float\n",
                    "\n",
                    "    class Config:\n",
                    "        orm_mode = True\n",
                    "\n",
                ]
            )

        if "CartItem" in entities:
            lines.extend(
                [
                    "class CartItemCreate(BaseModel):\n",
                    "    user_id: int\n",
                    "    product_id: int\n",
                    "    quantity: int\n",
                    "\n",
                    "class CartItemRead(BaseModel):\n",
                    "    id: int\n",
                    "    user_id: int\n",
                    "    product_id: int\n",
                    "    quantity: int\n",
                    "\n",
                    "    class Config:\n",
                    "        orm_mode = True\n",
                    "\n",
                ]
            )

        if "Todo" in entities:
            lines.extend(
                [
                    "class TodoCreate(BaseModel):\n",
                    "    title: str\n",
                    "\n",
                    "class TodoRead(BaseModel):\n",
                    "    id: int\n",
                    "    title: str\n",
                    "    completed: bool\n",
                    "\n",
                    "    class Config:\n",
                    "        orm_mode = True\n",
                    "\n",
                ]
            )

        handled_entities = {"User", "Task", "Product", "Order", "CartItem", "Todo"}
        for entity in entities:
            if entity in handled_entities:
                continue
            lines.extend([
                f"class {entity}Create(BaseModel):\n",
                "    name: str\n",
                "    description: Optional[str] = None\n",
                "    category: Optional[str] = 'General'\n",
                "    status: Optional[str] = 'Active'\n",
                "\n",
                f"class {entity}Read(BaseModel):\n",
                "    id: int\n",
                "    name: str\n",
                "    description: Optional[str] = None\n",
                "    category: str\n",
                "    status: str\n",
                "\n",
                "    class Config:\n",
                "        orm_mode = True\n",
                "\n",
            ])

        if not lines:
            return ""
        return "".join(lines)

    def _services_content(self, entities: list[str], has_auth: bool) -> str:
        lines = [
            "from sqlalchemy.orm import Session\n",
            "\n",
        ]

        if has_auth or "Task" in entities or "Order" in entities or "CartItem" in entities or "Todo" in entities:
            lines.append("from app.models.models import User\n")
        if "Task" in entities:
            lines.append("from app.models.models import Task\n")
        if "Product" in entities:
            lines.append("from app.models.models import Product\n")
        if "Order" in entities:
            lines.append("from app.models.models import Order\n")
        if "CartItem" in entities:
            lines.append("from app.models.models import CartItem\n")
        if "Todo" in entities:
            lines.append("from app.models.models import Todo\n")
        handled_entities = {"User", "Task", "Product", "Order", "CartItem", "Todo"}
        generic_entities = [entity for entity in entities if entity not in handled_entities]
        if generic_entities:
            lines.append(f"from app.models.models import {', '.join(generic_entities)}\n")

        lines.append("\n")

        if has_auth:
            lines.extend(
                [
                    "def get_user_by_email(db: Session, email: str) -> User | None:\n",
                    "    return db.query(User).filter(User.email == email).first()\n",
                    "\n",
                    "def create_user(db: Session, email: str, hashed_password: str) -> User:\n",
                    "    user = User(email=email, hashed_password=hashed_password)\n",
                    "    db.add(user)\n",
                    "    db.commit()\n",
                    "    db.refresh(user)\n",
                    "    return user\n",
                    "\n",
                ]
            )

        if "Task" in entities:
            lines.extend(
                [
                    "def get_tasks(db: Session, user_id: int) -> list[Task]:\n",
                    "    return db.query(Task).filter(Task.owner_id == user_id).all()\n",
                    "\n",
                    "def create_task(db: Session, title: str, description: str | None, owner_id: int) -> Task:\n",
                    "    task = Task(title=title, description=description, owner_id=owner_id)\n",
                    "    db.add(task)\n",
                    "    db.commit()\n",
                    "    db.refresh(task)\n",
                    "    return task\n",
                    "\n",
                ]
            )

        if "Product" in entities:
            lines.extend(
                [
                    "def get_products(db: Session) -> list[Product]:\n",
                    "    return db.query(Product).filter(Product.available == True).all()\n",
                    "\n",
                    "def create_product(db: Session, name: str, description: str | None, price: float) -> Product:\n",
                    "    product = Product(name=name, description=description, price=price)\n",
                    "    db.add(product)\n",
                    "    db.commit()\n",
                    "    db.refresh(product)\n",
                    "    return product\n",
                    "\n",
                ]
            )

        if "Order" in entities:
            lines.extend(
                [
                    "def get_orders(db: Session, user_id: int) -> list[Order]:\n",
                    "    return db.query(Order).filter(Order.user_id == user_id).all()\n",
                    "\n",
                    "def create_order(db: Session, user_id: int, total_amount: float) -> Order:\n",
                    "    order = Order(user_id=user_id, total_amount=total_amount)\n",
                    "    db.add(order)\n",
                    "    db.commit()\n",
                    "    db.refresh(order)\n",
                    "    return order\n",
                    "\n",
                ]
            )

        if "CartItem" in entities:
            lines.extend(
                [
                    "def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int) -> CartItem:\n",
                    "    cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)\n",
                    "    db.add(cart_item)\n",
                    "    db.commit()\n",
                    "    db.refresh(cart_item)\n",
                    "    return cart_item\n",
                    "\n",
                ]
            )

        if "Todo" in entities:
            lines.extend(
                [
                    "def get_todos(db: Session, user_id: int) -> list[Todo]:\n",
                    "    return db.query(Todo).filter(Todo.owner_id == user_id).all()\n",
                    "\n",
                    "def create_todo(db: Session, title: str, owner_id: int) -> Todo:\n",
                    "    todo = Todo(title=title, owner_id=owner_id)\n",
                    "    db.add(todo)\n",
                    "    db.commit()\n",
                    "    db.refresh(todo)\n",
                    "    return todo\n",
                    "\n",
                ]
            )

        for entity in generic_entities:
            function_name = self._snake_case(entity)
            lines.extend([
                f"def get_{self._plural_name(function_name)}(db: Session) -> list[{entity}]:\n",
                f"    return db.query({entity}).all()\n",
                "\n",
                f"def create_{function_name}(db: Session, name: str, description: str | None) -> {entity}:\n",
                f"    item = {entity}(name=name, description=description)\n",
                "    db.add(item)\n",
                "    db.commit()\n",
                "    db.refresh(item)\n",
                "    return item\n",
                "\n",
            ])

        return "".join(lines)

    def _routers_content(self, entities: list[str], has_auth: bool, requires_database: bool) -> str:
        lines = [
            "from fastapi import APIRouter, Depends, HTTPException, status\n",
        ]
        if has_auth:
            lines.append("from fastapi.security import OAuth2PasswordBearer\n")

        if requires_database:
            lines.append("from sqlalchemy.orm import Session\n")
            lines.append("from app.database.connection import get_db\n")
            model_names = [entity for entity in entities if entity != "User"]
            if has_auth and "User" in entities:
                model_names.insert(0, "User")
            if model_names:
                lines.append(f"from app.models.models import {', '.join(model_names)}\n")

        if has_auth:
            lines.append("from app.auth.jwt import create_access_token\n")
            lines.append("from app.schemas.schemas import LoginRequest, Token, UserCreate, UserRead\n")

        if "Task" in entities:
            lines.append("from app.schemas.schemas import TaskCreate, TaskRead\n")
        if "Product" in entities:
            lines.append("from app.schemas.schemas import ProductCreate, ProductRead\n")
        if "Order" in entities:
            lines.append("from app.schemas.schemas import OrderCreate, OrderRead\n")
        if "CartItem" in entities:
            lines.append("from app.schemas.schemas import CartItemCreate, CartItemRead\n")
        if "Todo" in entities:
            lines.append("from app.schemas.schemas import TodoCreate, TodoRead\n")
        generic_entities = [
            entity for entity in entities
            if entity not in {"User", "Task", "Product", "Order", "CartItem", "Todo"}
        ]
        for entity in generic_entities:
            lines.append(f"from app.schemas.schemas import {entity}Create, {entity}Read\n")

        if requires_database:
            service_imports = []
            if has_auth:
                service_imports.extend(["get_user_by_email", "create_user"])
            if "Task" in entities:
                service_imports.extend(["get_tasks", "create_task"])
            if "Product" in entities:
                service_imports.extend(["get_products", "create_product"])
            if "Order" in entities:
                service_imports.extend(["get_orders", "create_order"])
            if "CartItem" in entities:
                service_imports.append("add_to_cart")
            if "Todo" in entities:
                service_imports.extend(["get_todos", "create_todo"])

            if service_imports:
                imports = ", ".join(service_imports)
                lines.append(f"from app.services.services import {imports}\n")

        lines.append("\n")
        lines.append("router = APIRouter()\n")
        lines.append("\n")
        lines.append("@router.get('/health')\n")
        lines.append("async def health_check() -> dict[str, str]:\n")
        lines.append("    return {'status': 'ok'}\n")
        lines.append("\n")

        if requires_database:
            if has_auth:
                lines.extend([
                    "oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')\n",
                    "\n",
                    "def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:\n",
                    "    email = token.split(':', 1)[0]\n",
                    "    user = get_user_by_email(db, email)\n",
                    "    if user is None:\n",
                    "        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication token')\n",
                    "    return user\n",
                    "\n",
                ])
            lines.extend([
                "@router.get('/counts')\n",
                "def database_counts(db: Session = Depends(get_db)"
                + (", current_user: User = Depends(get_current_user)" if has_auth else "")
                + ") -> dict[str, int]:\n",
                "    counts = {\n",
            ])
            for entity in entities:
                if entity == "User":
                    continue
                route_name = re.sub(r"[^a-z0-9]", "", self._plural_name(self._snake_case(entity)))
                query = f"db.query({entity})"
                if has_auth:
                    query += f".filter({entity}.created_by_id == current_user.id)"
                lines.append(f"        {route_name!r}: {query}.count(),\n")
            lines.extend([
                "    }\n",
                "    counts['total'] = sum(counts.values())\n",
                "    return counts\n",
                "\n",
            ])

        if has_auth:
            lines.extend(
                [
                    "@router.post('/login', response_model=Token)\n",
                    "def login(request: LoginRequest, db: Session = Depends(get_db)): \n",
                    "    user = get_user_by_email(db, request.email)\n",
                    "    if not user or user.hashed_password != request.password:\n",
                    "        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')\n",
                    "    access_token = create_access_token(request.email)\n",
                    "    return {'access_token': access_token, 'token_type': 'bearer'}\n",
                    "\n",
                    "@router.post('/api/login', response_model=Token)\n",
                    "def api_login(request: LoginRequest, db: Session = Depends(get_db)): \n",
                    "    return login(request, db)\n",
                    "\n",
                ]
            )
            lines.extend(
                [
                    "@router.post('/register', response_model=UserRead)\n",
                    "def register(request: UserCreate, db: Session = Depends(get_db)): \n",
                    "    existing = get_user_by_email(db, request.email)\n",
                    "    if existing:\n",
                    "        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')\n",
                    "    user = create_user(db, request.email, request.password)\n",
                    "    return user\n",
                    "\n",
                    "@router.post('/api/register', response_model=UserRead)\n",
                    "def api_register(request: UserCreate, db: Session = Depends(get_db)): \n",
                    "    return register(request, db)\n",
                    "\n",
                ]
            )

        if "Task" in entities:
            lines.extend(
                [
                    "@router.get('/tasks', response_model=list[TaskRead])\n",
                    "def list_tasks(db: Session = Depends(get_db)): \n",
                    "    return get_tasks(db, user_id=1)\n",
                    "\n",
                    "@router.post('/tasks', response_model=TaskRead)\n",
                    "def create_task_route(request: TaskCreate, db: Session = Depends(get_db)): \n",
                    "    return create_task(db, request.title, request.description, owner_id=1)\n",
                    "\n",
                ]
            )

        if "Product" in entities:
            lines.extend(
                [
                    "@router.get('/products', response_model=list[ProductRead])\n",
                    "def list_products(db: Session = Depends(get_db)): \n",
                    "    return get_products(db)\n",
                    "\n",
                ]
            )

        if "Order" in entities:
            lines.extend(
                [
                    "@router.get('/orders', response_model=list[OrderRead])\n",
                    "def list_orders(db: Session = Depends(get_db)): \n",
                    "    return get_orders(db, user_id=1)\n",
                    "\n",
                ]
            )

        if "CartItem" in entities:
            lines.extend(
                [
                    "@router.post('/cart', response_model=CartItemRead)\n",
                    "def add_cart_item(request: CartItemCreate, db: Session = Depends(get_db)): \n",
                    "    return add_to_cart(db, request.user_id, request.product_id, request.quantity)\n",
                    "\n",
                ]
            )

        if "Todo" in entities:
            lines.extend(
                [
                    "@router.get('/todos', response_model=list[TodoRead])\n",
                    "def list_todos(db: Session = Depends(get_db)): \n",
                    "    return get_todos(db, user_id=1)\n",
                    "\n",
                    "@router.post('/todos', response_model=TodoRead)\n",
                    "def create_todo_route(request: TodoCreate, db: Session = Depends(get_db)): \n",
                    "    return create_todo(db, request.title, owner_id=1)\n",
                    "\n",
                ]
            )

        for entity in generic_entities:
            route = self._plural_name(self._snake_case(entity))
            user_dependency = ", current_user: User = Depends(get_current_user)" if has_auth else ""
            ownership = ", created_by_id=current_user.id" if has_auth else ""
            lines.extend([
                f"@router.get('/{route}', response_model=list[{entity}Read])\n",
                f"def list_{route}(db: Session = Depends(get_db){user_dependency}):\n",
                f"    query = db.query({entity})\n",
            ])
            if has_auth:
                lines.append(f"    query = query.filter({entity}.created_by_id == current_user.id)\n")
            lines.extend([
                "    return query.order_by("
                f"{entity}.created_at.desc()).all()\n",
                "\n",
                f"@router.post('/{route}', response_model={entity}Read)\n",
                f"def create_{self._snake_case(entity)}(request: {entity}Create, db: Session = Depends(get_db){user_dependency}):\n",
                f"    item = {entity}(name=request.name, description=request.description, category=request.category or 'General', status=request.status or 'Active'{ownership})\n",
                "    db.add(item)\n",
                "    db.commit()\n",
                "    db.refresh(item)\n",
                "    return item\n",
                "\n",
            ])

        return "".join(lines)

    def _auth_jwt_content(self) -> str:
        return (
            "from datetime import datetime, timedelta\n"
            "\n"
            "SECRET_KEY = 'change-me'\n"
            "ALGORITHM = 'HS256'\n"
            "ACCESS_TOKEN_EXPIRE_MINUTES = 60\n"
            "\n"
            "def create_access_token(email: str) -> str:\n"
            "    expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)\n"
            "    return f'{email}:{int(expiry.timestamp())}'\n"
        )

    @staticmethod
    def _snake_case(value: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()

    @staticmethod
    def _plural_name(value: str) -> str:
        if value.endswith(("s", "x")) and value.endswith("ss"):
            return value + "es"
        if value.endswith(("sh", "ch", "x", "z")):
            return value + "es"
        if value.endswith("y") and not value.endswith(("ay", "ey", "oy", "uy")):
            return value[:-1] + "ies"
        if value.endswith("s"):
            return value
        return value + "s"

    def _main_content(self, has_auth: bool, requires_database: bool = True) -> str:
        lines = [
            "from fastapi import FastAPI\n",
            "from fastapi.middleware.cors import CORSMiddleware\n",
        ]
        if requires_database:
            lines.extend([
                "from app.database.connection import engine\n",
                "from app.models.models import Base\n",
                "Base.metadata.create_all(bind=engine)\n",
            ])
        lines.extend([
            "from app.routers.routes import router\n",
            "\n",
            "app = FastAPI(title='Generated FastAPI Backend')\n",
            "app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=False, allow_methods=['*'], allow_headers=['*'])\n",
            "app.include_router(router)\n",
            "\n",
            "@app.get('/')\n",
            "async def read_root() -> dict[str, str]:\n",
            "    return {'message': 'Generated backend is running'}\n",
        ])
        return "".join(lines)

    def _package_init_content(self) -> str:
        return "# Package initialization\n"

    def _requirements_content(self, has_postgres: bool) -> str:
        requirements = [
            "fastapi>=0.110,<1.0",
            "uvicorn[standard]>=0.27,<1.0",
            "SQLAlchemy>=2.0,<3.0",
        ]
        if has_postgres:
            requirements.append("psycopg2-binary>=2.9,<3.0")
        return "\n".join(requirements) + "\n"

    def _validate_generated_files(self, generated_files: list[GeneratedFile]) -> None:
        seen_paths: set[str] = set()
        for generated_file in generated_files:
            path = generated_file.path.strip()
            if not path:
                raise ValueError("Generated file path is missing or empty.")
            if path in seen_paths:
                raise ValueError(f"Duplicate generated file path detected: {path}")
            seen_paths.add(path)

            content = generated_file.content
            if content is None or not content.strip():
                raise ValueError(f"Generated file '{path}' contains no content.")
            if "```" in content:
                raise ValueError(f"Generated file '{path}' contains markdown code fences.")

            if path.endswith(".py"):
                try:
                    ast.parse(content)
                except SyntaxError as exc:
                    raise ValueError(
                        f"Generated Python file '{path}' contains syntax errors: {exc.msg} (line {exc.lineno}, col {exc.offset})"
                    ) from exc
