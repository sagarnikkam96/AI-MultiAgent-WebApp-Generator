# TypeScript — Types

Using TypeScript types to add safety to the generated React frontend.

## Why types

TypeScript catches type errors at compile time and makes the data contracts between
frontend and backend explicit.

## Primitive and union types

```ts
type Status = "idle" | "loading" | "success" | "error";
type UserId = number;
```

## Object types via `type` aliases

```ts
type User = {
  id: number;
  email: string;
  role: "admin" | "patient" | "doctor";
  active: boolean;
};
```

## Nullable / optional fields

- Use `?` for optional properties: `{ nickname?: string }`.
- Use `T | null` or `T | undefined` for explicit nullability.

## Array types

```ts
type Users = User[];
// or
type UsersAlt = Array<User>;
```

## Literal and discriminated unions

Discriminated unions help model variants (e.g. different API payload shapes) safely by
switching on a common literal field.

```ts
type Event =
  | { kind: "login"; userId: number }
  | { kind: "error"; message: string };

function handle(e: Event) {
  if (e.kind === "login") {
    console.log(e.userId);
  }
}
```

## Utility types

Use built-in helpers when useful: `Partial<T>`, `Pick<T, K>`, `Omit<T, K>`,
`Record<K, V>`, `Readonly<T>`.

## no-explicit-any

Avoid `any`; use `unknown` and narrow, or define a precise type. This keeps generated code
type-safe and maintainable.
