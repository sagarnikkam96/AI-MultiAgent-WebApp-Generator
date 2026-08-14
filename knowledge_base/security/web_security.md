# Security — Web Security

Core web-security practices for generated web applications.

## HTTPS everywhere

Serve all traffic over HTTPS in production so data (including tokens) is encrypted in
transit. Do not send credentials or JWTs over plain HTTP.

## Input validation

- Validate and sanitise all user input server-side (Pydantic schemas).
- Never trust client-supplied data; always constrain types, lengths, and ranges.

## Authentication & sessions

- Hash and salt passwords; never store plaintext.
- Use short-lived tokens with proper expiry.
- Implement secure logout (invalidate the token).

## Security headers

Use standard response headers when possible:
- `Content-Security-Policy` — restrict resource loading.
- `X-Content-Type-Options: nosniff`.
- `X-Frame-Options` (or CSP `frame-ancestors`) — clickjacking protection.
- `Referrer-Policy`.

## Secrets handling

- Keep secrets (DB credentials, JWT secret) in environment configuration.
- Never hard-code secrets in source or commit them.

## Dependency hygiene

- Keep dependencies updated and pinned.
- Avoid unnecessary dependencies (fewer attack-surface packages).

## Client-side concerns (React)

- Escape/encode dynamic content when rendering to prevent XSS; React does this by default
  for text content — avoid `dangerouslySetInnerHTML` unless strictly necessary.
- Do not expose secrets in the frontend bundle; use `VITE_*` env vars for non-secret config.

## Least privilege

- Grant the DB user only the privileges it needs.
- Scope API tokens/roles to the minimum required.
