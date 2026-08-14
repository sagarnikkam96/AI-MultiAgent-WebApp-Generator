# Security — API Security

Protecting the REST API endpoints from common attacks.

## Authentication on protected routes

- Require a valid token on all protected endpoints.
- Use a `get_current_user` dependency; reject with `401` when invalid.
- Reject with `403` when an authenticated user is not authorised for an action.

## SQL injection prevention

- Always use the ORM or parameterised queries.
- Never build SQL by string-concatenating user input.
- SQLAlchemy binds parameters safely when you use query filters / bind params.

## Cross-Origin Resource Sharing (CORS)

- Restrict `allow_origins` to known frontend origins (e.g. `http://localhost:5173`).
- Do not use `*` for credentials-enabled requests.
- Only `allow_headers`/`allow_methods` that are actually needed.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Rate limiting and abuse

- Add rate limiting to sensitive endpoints (login, signup) to slow brute force.
- Validate request sizes and reject oversized payloads.

## Validation of inputs and parameters

- Validate path/query parameters and request bodies.
- Return `422`/`400` for malformed input instead of crashing.

## Error handling

- Return generic, non-revealing error messages to clients.
- Log detailed errors server-side; do not leak stack traces to the client.

## Path traversal protection

- For file-serving endpoints, validate and resolve paths so clients cannot escape the
  intended directory (see the backend's `_resolve_project_dir` path checks).

## Tokens in headers

- Send JWTs via the `Authorization: Bearer` header, never in URLs or logs.
