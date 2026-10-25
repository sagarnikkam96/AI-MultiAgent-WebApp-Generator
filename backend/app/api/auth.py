"""FastAPI authentication router for registration, login, and session validation."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from ..database.auth_db import (
    authenticate_user,
    get_user_by_id,
    register_user,
    verify_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, description="Unique username")
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")
    full_name: Optional[str] = Field(default="", description="Optional display name")


class LoginRequest(BaseModel):
    login: str = Field(..., description="Email address or username")
    password: str = Field(..., description="Password")


def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict[str, Any]:
    """Dependency that extracts and validates the Bearer token from the request header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please sign in.",
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'.",
        )
    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please sign in again.",
        )
    user = get_user_by_id(payload["uid"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
        )
    return user


def get_optional_current_user(authorization: Optional[str] = Header(default=None)) -> Optional[dict[str, Any]]:
    """Resolve a valid signed-in user when a bearer token is provided."""
    if not authorization:
        return None
    return get_current_user(authorization)


@router.post("/register")
def register(req: RegisterRequest) -> dict[str, Any]:
    """Register a new user account in SQLite."""
    try:
        user_data = register_user(
            username=req.username,
            email=req.email,
            password=req.password,
            full_name=req.full_name or "",
        )
        return {
            "status": "success",
            "message": "Account created successfully.",
            "user": {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
            },
            "token": user_data["token"],
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/login")
def login(req: LoginRequest) -> dict[str, Any]:
    """Authenticate an existing user and issue a signed session token."""
    try:
        user_data = authenticate_user(
            login_identifier=req.login,
            password=req.password,
        )
        return {
            "status": "success",
            "message": "Signed in successfully.",
            "user": {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
            },
            "token": user_data["token"],
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


@router.get("/me")
def get_me(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """Return the profile of the currently signed-in user."""
    return {
        "status": "success",
        "user": {
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "full_name": current_user["full_name"],
            "created_at": current_user["created_at"],
        },
    }


@router.post("/logout")
def logout() -> dict[str, Any]:
    """Sign out endpoint."""
    return {"status": "success", "message": "Signed out successfully."}
