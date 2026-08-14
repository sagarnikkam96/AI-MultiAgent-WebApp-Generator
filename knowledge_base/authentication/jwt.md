# Authentication — JWT

JSON Web Token (JWT) based authentication for generated backends.

## What JWT is

A JWT is a signed, compact token containing claims. It is commonly used for stateless
authentication: the server issues a token on login and the client sends it on subsequent
requests via the `Authorization` header.

## Token structure

A JWT has three parts, dot-separated:
`<header>.<payload>.<signature>`

- **Header**: algorithm + token type (`{"alg": "HS256", "typ": "JWT"}`).
- **Payload**: claims (e.g. `sub` = user id, `exp` = expiry, `iat` = issued-at).
- **Signature**: verifies the token was issued by the server.

## Issuing a token on login

```
1. POST /auth/login  with credentials
2. Server verifies credentials (password hash)
3. Server signs a JWT with the user id and expiry
4. Client stores the token and sends it as Bearer on later requests
```

## Sending the token

```
Authorization: Bearer <token>
```

The backend extracts and verifies the token on protected routes.

## Verification on protected routes

```
1. Parse the Authorization header (expect "Bearer <token>").
2. Verify the signature and expiry.
3. Load claims (e.g. sub) to identify the user.
4. Reject with 401 if missing/invalid/expired.
```

## Security notes

- Sign with a strong, secret key; keep it in server configuration (`.env`), not in code.
- Set a reasonable `exp` (expiry) and validate it.
- Never put sensitive data (passwords) in the token payload.
- Use HTTPS in production so tokens are not sent in plaintext.
- Store the secret and prefer hashed passwords using a strong algorithm.
