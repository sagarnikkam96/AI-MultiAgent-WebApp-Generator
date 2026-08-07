from __future__ import annotations

import ast
import re
from typing import Protocol

from .code_generator import CodeGenerator, PromptProvider
from .code_schema import GeneratedFile


class BackendGenerator(CodeGenerator):
    """Generates backend code artifacts for Version 2."""

    def generate_files(self, prompt_provider: PromptProvider) -> list[GeneratedFile]:
        """Create backend files from the given prompt provider."""
        prompt = prompt_provider.get_prompt()
        generated_files = self._build_backend_files(prompt)
        self._validate_generated_files(generated_files)
        return generated_files

    def _build_backend_files(self, prompt: str) -> list[GeneratedFile]:
        """Construct the backend file list based on natural language requirements."""
        requirements = prompt.strip()
        project_slug = self._project_slug(requirements)
        project_root = f"generated_projects/{project_slug}/backend"
        has_postgres = self._requires_postgres(requirements)
        has_auth = self._requires_auth(requirements)
        entities = self._extract_entities(requirements)

        if has_auth and "User" not in entities:
            entities.insert(0, "User")

        requires_database = has_postgres or bool(entities)
        generated_files: list[GeneratedFile] = []

        if requires_database:
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/database/connection.py",
                    content=self._database_connection_content(has_postgres),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/database/session.py",
                    content=self._database_session_content(),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/database/__init__.py",
                    content=self._package_init_content(),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/models/models.py",
                    content=self._models_content(entities, has_auth),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/models/__init__.py",
                    content=self._package_init_content(),
                )
            )

        generated_files.append(
            GeneratedFile(
                path=f"{project_root}/schemas/schemas.py",
                content=self._schemas_content(entities, has_auth),
            )
        )
        generated_files.append(
            GeneratedFile(
                path=f"{project_root}/schemas/__init__.py",
                content=self._package_init_content(),
            )
        )

        if requires_database:
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/services/services.py",
                    content=self._services_content(entities, has_auth),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/services/__init__.py",
                    content=self._package_init_content(),
                )
            )

        generated_files.append(
            GeneratedFile(
                path=f"{project_root}/routers/routes.py",
                content=self._routers_content(entities, has_auth, requires_database),
            )
        )
        generated_files.append(
            GeneratedFile(
                path=f"{project_root}/routers/__init__.py",
                content=self._package_init_content(),
            )
        )

        if has_auth:
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/auth/jwt.py",
                    content=self._auth_jwt_content(),
                )
            )
            generated_files.append(
                GeneratedFile(
                    path=f"{project_root}/auth/__init__.py",
                    content=self._package_init_content(),
                )
            )

        generated_files.append(
            GeneratedFile(
                path=f"{project_root}/main.py",
                content=self._main_content(has_auth),
            )
        )

        return generated_files

    def _project_slug(self, requirements: str) -> str:
        text = requirements.lower()
        text = re.sub(r"[^a-z0-9\s-]", " ", text)
        text = re.sub(
            r"\b(build|create|generate|develop|design|application|app|system|using|with|and|or|for|the|a|an|react|fastapi|postgres|postgresql|login|signup|register|authentication|auth|jwt|token|users|user|tasks|task|patients|doctors|billing|products|cart|orders)\b",
            " ",
            text,
        )
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return "generated_project"
        slug = "_".join(text.split()[:4])
        return slug[:50].strip("_") or "generated_project"

    def _table_name(self, entity: str) -> str:
        lower_entity = entity.lower()
        if lower_entity.endswith("y") and not lower_entity.endswith("ay") and not lower_entity.endswith("ey"):
            return lower_entity[:-1] + "ies"
        if lower_entity.endswith("s"):
            return lower_entity
        return lower_entity + "s"

    def _pluralize(self, entity: str) -> str:
        lower_entity = entity.lower()
        if lower_entity.endswith("y") and not lower_entity.endswith("ay") and not lower_entity.endswith("ey"):
            return lower_entity[:-1] + "ies"
        if lower_entity.endswith("s"):
            return lower_entity + "es"
        return lower_entity + "s"

    def _titleize(self, value: str) -> str:
        return "".join(word.capitalize() for word in re.split(r"[_\s-]+", value))

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
            "carts": "CartItem",
            "user": "User",
            "users": "User",
            "customer": "Customer",
            "customers": "Customer",
            "doctor": "Doctor",
            "doctors": "Doctor",
            "patient": "Patient",
            "patients": "Patient",
            "billing": "Billing",
            "invoice": "Invoice",
            "invoices": "Invoice",
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
            "appointment": "Appointment",
            "appointments": "Appointment",
            "category": "Category",
            "categories": "Category",
        }

        stopwords = {
            "build",
            "create",
            "generate",
            "develop",
            "design",
            "application",
            "app",
            "system",
            "using",
            "with",
            "and",
            "or",
            "for",
            "the",
            "a",
            "an",
            "react",
            "fastapi",
            "postgres",
            "postgresql",
            "login",
            "signup",
            "register",
            "authentication",
            "auth",
            "jwt",
            "token",
            "management",
            "managements",
            "dashboard",
            "backend",
            "frontend",
            "user",
            "users",
            "task",
            "tasks",
        }

        entities: list[str] = []
        for keyword, entity_name in entity_map.items():
            if re.search(rf"\b{re.escape(keyword)}\b", text) and entity_name not in entities:
                entities.append(entity_name)

        if not entities:
            candidates = re.findall(r"\b[a-zA-Z]{4,}\b", text)
            for candidate in candidates:
                if candidate in stopwords or candidate.isnumeric():
                    continue
                if candidate in entity_map:
                    continue
                camelized = self._titleize(candidate)
                if camelized not in entities:
                    entities.append(camelized)

        return entities

    def _database_connection_content(self, use_postgres: bool) -> str:
        if use_postgres:
            return (
                "import os\n"
                "from sqlalchemy import create_engine\n"
                "from sqlalchemy.orm import sessionmaker\n"
                "\n"
                "DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/app_db')\n"
                "engine = create_engine(DATABASE_URL, future=True)\n"
                "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)\n"
                "\n"
                "def get_db():\n"
                "    db = SessionLocal()\n"
                "    try:\n"
                "        yield db\n"
                "    finally:\n"
                "        db.close()\n"
            )

        return (
            "import os\n"
            "from sqlalchemy import create_engine\n"
            "from sqlalchemy.orm import sessionmaker\n"
            "\n"
            "DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app.db')\n"
            "engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False}, future=True)\n"
            "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)\n"
            "\n"
            "def get_db():\n"
            "    db = SessionLocal()\n"
            "    try:\n"
            "        yield db\n"
            "    finally:\n"
            "        db.close()\n"
        )

    def _database_session_content(self) -> str:
        return (
            "from sqlalchemy import create_engine\n"
            "from sqlalchemy.orm import sessionmaker\n"
            "import os\n"
            "\n"
            "DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app.db')\n"
            "engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False}, future=True)\n"
            "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)\n"
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
            "from datetime import datetime\n",
            "from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text\n",
            "from sqlalchemy.orm import declarative_base, relationship\n",
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
                    "    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)\n",
                    "\n",
                ]
            )

        for entity in entities:
            if entity == "User":
                continue

            table_name = self._table_name(entity)
            lines.extend(
                [
                    f"class {entity}(Base):\n",
                    f"    __tablename__ = '{table_name}'\n",
                    "    id = Column(Integer, primary_key=True, index=True)\n",
                    "    name = Column(String, nullable=False)\n",
                    "    description = Column(Text, nullable=True)\n",
                    "    is_active = Column(Boolean, default=True, nullable=False)\n",
                    "    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)\n",
                    "    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)\n",
                ]
            )

            if has_auth:
                lines.extend(
                    [
                        "    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)\n",
                        "    created_by = relationship('User')\n",
                    ]
                )

            lines.append("\n")

        return "".join(lines)

    def _schemas_content(self, entities: list[str], has_auth: bool) -> str:
        lines = [
            "from datetime import datetime\n",
            "from typing import Optional\n",
            "from pydantic import BaseModel\n",
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
                    "    created_at: datetime\n",
                    "    updated_at: datetime\n",
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

        for entity in entities:
            if entity == "User":
                continue

            entity_create = f"{entity}Create"
            entity_read = f"{entity}Read"
            lines.extend(
                [
                    f"class {entity_create}(BaseModel):\n",
                    "    name: str\n",
                    "    description: Optional[str] = None\n",
                    "\n",
                    f"class {entity_read}(BaseModel):\n",
                    "    id: int\n",
                    "    name: str\n",
                    "    description: Optional[str] = None\n",
                    "    is_active: bool\n",
                    "    created_at: datetime\n",
                    "    updated_at: datetime\n",
                ]
            )
            if has_auth:
                lines.append("    created_by_id: Optional[int] = None\n")
            lines.extend(
                [
                    "\n",
                    "    class Config:\n",
                    "        orm_mode = True\n",
                    "\n",
                ]
            )

        return "".join(lines)

    def _services_content(self, entities: list[str], has_auth: bool) -> str:
        lines = [
            "from sqlalchemy.orm import Session\n",
            "\n",
        ]

        if has_auth:
            lines.append("from models.models import User\n")

        for entity in entities:
            if entity == "User":
                continue
            lines.append(f"from models.models import {entity}\n")

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

        for entity in entities:
            if entity == "User":
                continue

            plural_name = self._pluralize(entity).lower()
            lines.extend(
                [
                    f"def get_{plural_name}(db: Session, created_by_id: int | None = None) -> list[{entity}]:\n",
                    "    query = db.query({0})\n".format(entity),
                    "    if created_by_id is not None:\n",
                    "        query = query.filter({0}.created_by_id == created_by_id)\n".format(entity),
                    "    return query.all()\n",
                    "\n",
                    f"def create_{entity.lower()}(db: Session, name: str, description: str | None = None, created_by_id: int | None = None) -> {entity}:\n",
                    "    item = {0}(name=name, description=description, created_by_id=created_by_id)\n".format(entity),
                    "    db.add(item)\n",
                    "    db.commit()\n",
                    "    db.refresh(item)\n",
                    "    return item\n",
                    "\n",
                ]
            )

        return "".join(lines)

    def _routers_content(self, entities: list[str], has_auth: bool, requires_database: bool) -> str:
        lines = [
            "from fastapi import APIRouter, Depends, HTTPException, status\n",
        ]

        if requires_database:
            lines.append("from sqlalchemy.orm import Session\n")
            lines.append("from database.connection import get_db\n")

        if has_auth:
            lines.append(
                "from fastapi.security import OAuth2PasswordBearer\n"
                "from auth.jwt import create_access_token, hash_password, verify_access_token, verify_password\n"
                "from models.models import User\n"
                "from schemas.schemas import LoginRequest, Token, UserCreate, UserRead\n"
            )

        for entity in entities:
            if entity == "User":
                continue
            lines.append(f"from schemas.schemas import {entity}Create, {entity}Read\n")

        if requires_database:
            service_imports = []
            if has_auth:
                service_imports.extend(["get_user_by_email", "create_user"])
            for entity in entities:
                if entity == "User":
                    continue
                plural_name = self._pluralize(entity).lower()
                service_imports.extend([f"get_{plural_name}", f"create_{entity.lower()}"])

            imports = ", ".join(service_imports)
            lines.append(f"from services.services import {imports}\n")

        lines.append("\n")
        lines.append("oauth2_scheme = OAuth2PasswordBearer(tokenUrl=\"/api/login\")\n")
        lines.append("router = APIRouter(prefix=\"/api\")\n")
        lines.append("\n")
        lines.append("@router.get('/health')\n")
        lines.append("async def health_check() -> dict[str, str]:\n")
        lines.append("    return {'status': 'ok'}\n")
        lines.append("\n")

        if has_auth:
            lines.extend(
                [
                    "def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:\n",
                    "    payload = verify_access_token(token)\n",
                    "    email = payload.get('sub')\n",
                    "    if not email:\n",
                    "        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication token')\n",
                    "    user = get_user_by_email(db, email)\n",
                    "    if not user:\n",
                    "        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid user credentials')\n",
                    "    return user\n",
                    "\n",
                    "@router.post('/login', response_model=Token)\n",
                    "def login(request: LoginRequest, db: Session = Depends(get_db)): \n",
                    "    user = get_user_by_email(db, request.email)\n",
                    "    if not user or not verify_password(request.password, user.hashed_password):\n",
                    "        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')\n",
                    "    access_token = create_access_token(user.email)\n",
                    "    return {'access_token': access_token, 'token_type': 'bearer'}\n",
                    "\n",
                    "@router.post('/register', response_model=UserRead)\n",
                    "def register(request: UserCreate, db: Session = Depends(get_db)): \n",
                    "    existing = get_user_by_email(db, request.email)\n",
                    "    if existing:\n",
                    "        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')\n",
                    "    user = create_user(db, request.email, hash_password(request.password))\n",
                    "    return user\n",
                    "\n",
                ]
            )

        for entity in entities:
            if entity == "User":
                continue

            plural_route = self._pluralize(entity).lower()
            lines.extend(
                [
                    f"@router.get('/{plural_route}', response_model=list[{entity}Read])\n",
                    "def list_items(db: Session = Depends(get_db)" + (", current_user: User = Depends(get_current_user)" if has_auth else "") + "): \n",
                    ("    return get_{0}(db, created_by_id=current_user.id)\n" if has_auth else "    return get_{0}(db)\n").format(plural_route),
                    "\n",
                    f"@router.post('/{plural_route}', response_model={entity}Read)\n",
                    "def create_item(request: {0}Create, db: Session = Depends(get_db)".format(entity) + (", current_user: User = Depends(get_current_user)" if has_auth else "") + "): \n",
                    ("    return create_{0}(db, request.name, request.description, created_by_id=current_user.id)\n" if has_auth else "    return create_{0}(db, request.name, request.description)\n").format(entity.lower()),
                    "\n",
                ]
            )

        return "".join(lines)

    def _auth_jwt_content(self) -> str:
        return (
            "from __future__ import annotations\n"
            "import base64\n"
            "import hashlib\n"
            "import hmac\n"
            "import json\n"
            "import os\n"
            "from datetime import datetime, timedelta\n"
            "from typing import Any\n"
            "\n"
            "SECRET_KEY = os.getenv('SECRET_KEY', 'replace-this-secret')\n"
            "ALGORITHM = 'HS256'\n"
            "ACCESS_TOKEN_EXPIRE_MINUTES = 60\n"
            "\n"
            "def _urlsafe_b64encode(data: bytes) -> str:\n"
            "    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')\n"
            "\n"
            "def _urlsafe_b64decode(data: str) -> bytes:\n"
            "    padding = '=' * (-len(data) % 4)\n"
            "    return base64.urlsafe_b64decode(data + padding)\n"
            "\n"
            "def _sign(message: bytes) -> str:\n"
            "    signature = hmac.new(SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()\n"
            "    return _urlsafe_b64encode(signature)\n"
            "\n"
            "def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:\n"
            "    expires_delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)\n"
            "    payload = {'sub': subject, 'exp': int((datetime.utcnow() + expires_delta).timestamp())}\n"
            "    header = {'alg': ALGORITHM, 'typ': 'JWT'}\n"
            "    encoded_header = _urlsafe_b64encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))\n"
            "    encoded_payload = _urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))\n"
            "    signature = _sign(f'{encoded_header}.{encoded_payload}'.encode('utf-8'))\n"
            "    return f'{encoded_header}.{encoded_payload}.{signature}'\n"
            "\n"
            "def verify_access_token(token: str) -> dict[str, Any]:\n"
            "    try:\n"
            "        encoded_header, encoded_payload, signature = token.split('.')\n"
            "        expected = _sign(f'{encoded_header}.{encoded_payload}'.encode('utf-8'))\n"
            "        if not hmac.compare_digest(expected, signature):\n"
            "            raise ValueError('Invalid token signature')\n"
            "        payload = json.loads(_urlsafe_b64decode(encoded_payload).decode('utf-8'))\n"
            "        if int(payload.get('exp', 0)) < int(datetime.utcnow().timestamp()):\n"
            "            raise ValueError('Token has expired')\n"
            "        return payload\n"
            "    except (ValueError, json.JSONDecodeError):\n"
            "        raise ValueError('Invalid token')\n"
            "\n"
            "def hash_password(password: str) -> str:\n"
            "    salt = os.urandom(16)\n"
            "    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)\n"
            "    return f'{_urlsafe_b64encode(salt)}${_urlsafe_b64encode(hashed)}'\n"
            "\n"
            "def verify_password(password: str, hashed_password: str) -> bool:\n"
            "    try:\n"
            "        salt, expected = hashed_password.split('$', 1)\n"
            "        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), _urlsafe_b64decode(salt), 100000)\n"
            "        return hmac.compare_digest(_urlsafe_b64encode(hashed), expected)\n"
            "    except ValueError:\n"
            "        return False\n"
        )

    def _main_content(self, has_auth: bool) -> str:
        return (
            "from fastapi import FastAPI\n"
            "from routers.routes import router\n"
            "\n"
            "app = FastAPI(title='Generated FastAPI Backend')\n"
            "\n"
            "app.include_router(router)\n"
            "\n"
            "@app.get('/')\n"
            "async def read_root() -> dict[str, str]:\n"
            "    return {'message': 'Generated backend is running'}\n"
        )

    def _package_init_content(self) -> str:
        return "# Package initialization\n"

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
