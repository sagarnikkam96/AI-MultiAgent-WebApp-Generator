# TypeScript — Interfaces

Using interfaces to define contracts in the generated frontend.

## When to use interfaces

Interfaces are ideal for defining the **shape of objects** and can be extended and
implemented. Prefer interfaces for API response/request shapes and props contracts.

```ts
interface ApiUser {
  id: number;
  email: string;
  name: string;
}

interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: ApiUser;
}
```

## Props contracts

Every React component should define its props with an interface:

```tsx
interface DashboardProps {
  userName: string;
  onLogout: () => void;
}

export function Dashboard({ userName, onLogout }: DashboardProps) {
  // ...
}
```

## Extending interfaces

Compose interfaces with `extends`:

```ts
interface BaseEntity {
  id: number;
  createdAt: string;
}

interface Patient extends BaseEntity {
  name: string;
  condition: string;
}
```

## Describing API payloads

Mirror the backend response schemas so the frontend statically knows what the API returns.
Define an interface per endpoint response and per request body.

## Optional and readonly members

```ts
interface Config {
  readonly apiBaseUrl: string;
  maxRetries?: number;
}
```

## type vs interface

- Use `interface` for object shapes that may be extended.
- Use `type` aliases for unions, tuples, primitives, and function signatures.
Both are valid; keep usage consistent within the generated codebase.
