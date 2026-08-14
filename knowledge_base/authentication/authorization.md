# Authentication — Authorization

Enforcing roles and access control for generated applications.

## Authentication vs. authorization

- **Authentication**: verifying *who* the user is (login, token validation).
- **Authorization**: verifying *what* the user is allowed to do (roles/permissions).

## Roles

Assign each user a role (e.g. `admin`, `doctor`, `patient`).

```python
class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), nullable=False, default="user")
```

## Protecting routes

Require a valid authenticated user on protected endpoints; reject with `401` when the token
is missing/invalid and `403` when the user lacks permission.

```python
@app.get("/admin")
def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"ok": True}
```

## Common patterns

- **Current-user dependency**: a `get_current_user` dependency resolves the user from the
  JWT and is injected into protected routes.
- **Role checks**: guard admin/manager actions by role.
- **Resource ownership**: users can usually only access their own data (check `owner_id`).

## Frontend guidance

- Show/hide UI elements based on the logged-in user's role.
- Never rely on the frontend alone for security — the backend must enforce authorization.

## Rules of thumb

- Default-deny: require explicit permission for sensitive actions.
- Keep authorization checks on the backend (client-side checks are UX only).
- Return `403` for authenticated-but-forbidden, `401` for unauthenticated.
