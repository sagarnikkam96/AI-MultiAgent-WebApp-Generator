# REST API — Endpoints

Designing concrete REST endpoints for CRUD-style generated applications.

## Collection endpoints

```
GET    /users          # list users (filter/paginate via query params)
POST   /users          # create a user            -> 201 + created object
```

## Item endpoints

```
GET    /users/{id}     # read a single user       -> 200 or 404
PUT    /users/{id}     # replace a user           -> 200
PATCH  /users/{id}     # partial update           -> 200
DELETE /users/{id}     # delete a user            -> 204
```

## Nested / sub-resources

Use nested routes for tightly-coupled resources:

```
GET  /users/{user_id}/orders        # orders belonging to a user
POST /users/{user_id}/orders        # create an order for a user
```

## Request/response shape

- Accept and return JSON.
- Validate request bodies with schemas.
- Keep the response shape stable and documented.

## Example: appointments

```
POST   /appointments             body: { patient_id, doctor_id, slot }
GET    /appointments?patient_id=1
GET    /appointments/{id}
PATCH  /appointments/{id}
DELETE /appointments/{id}
```

## Common conventions in generated apps

- `GET /health` returns service status.
- Auth endpoints: `POST /auth/login`, `POST /auth/register`.
- Authenticated resources require a valid bearer token.
- Use `404` with a clear detail message when a resource is missing.

## Pagination envelope example

```json
{
  "items": [ ... ],
  "total": 120,
  "page": 1,
  "page_size": 20
}
```
