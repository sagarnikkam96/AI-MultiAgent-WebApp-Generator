# REST API — Principles

Core principles for designing consistent REST APIs.

## Resource-based

Model the API around **resources** (nouns) rather than actions (verbs in URLs).

- Bad: `GET /getUser`, `POST /deleteOrder`
- Good: `GET /users/{id}`, `DELETE /orders/{id}`

## HTTP methods

| Method | Purpose                          | Typical status |
| ------ | -------------------------------- | -------------- |
| GET    | Read a resource / collection     | 200            |
| POST   | Create a resource                | 201            |
| PUT    | Replace a resource               | 200            |
| PATCH  | Partial update                   | 200            |
| DELETE | Remove a resource                | 204            |

## Status codes

Use standard codes to communicate semantics: `200`, `201`, `204`, `400` (bad request),
`401` (unauthenticated), `403` (forbidden), `404` (not found), `422` (validation),
`500` (server error).

## Statelessness

Each request should be self-contained; the server does not keep client state between
requests. Authentication tokens carry identity per request.

## Consistent naming and plural nouns

- Use plural nouns for collections: `/users`, `/orders`, `/appointments`.
- Use hyphens or underscores consistently; lowercase is typical.

## Filtering, sorting, pagination

- Filter with query params: `GET /users?role=admin`.
- Paginate with `limit`/`offset` (or page-based) params.
- Return a structured envelope when paginating (items + count/next).

## Idempotency

- GET, PUT, DELETE should be idempotent (repeatable with same result).
- POST creates and is generally not idempotent.

## Versioning

Include an API version when breaking changes are expected (`/api/v1/...`).
