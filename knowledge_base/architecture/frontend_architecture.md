# Architecture — Frontend Architecture

Recommended frontend architecture for generated React + TypeScript Vite apps.

## High-level structure

```
src/
├── main.tsx         # React entrypoint
├── App.tsx          # Root component / app shell
├── routes/          # Route definitions
├── services/        # API client (fetch wrappers)
├── components/      # Reusable UI components
├── hooks/           # Custom React hooks
├── types/           # TypeScript interfaces/types
├── utils/           # Helper functions
└── styles/          # Global styles
```

## Data flow

- UI components render from state.
- Event handlers call API service functions.
- Services fetch from the backend and return typed responses.
- Components store/update state from the result and re-render.

## API service layer

Centralise network calls in a `services` module so components never call `fetch` directly:

```ts
// services/api.ts
export async function getUsers(): Promise<ApiUser[]> {
  const res = await fetch("/api/users");
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}
```

## Type safety

- Define interfaces for every API request/response payload (in `types/`).
- Type all component props.
- Keep the frontend types aligned with the backend schemas.

## Routing

- Use the route definitions to map URLs to page components.
- Keep the root layout (nav/header) in `App` and mount route content below it.

## State management

- Start with component-local `useState`.
- Lift state to shared ancestors or use Context for app-wide data (e.g. auth user).
- Avoid over-engineering; keep the generated frontend simple and maintainable.

## Styling

- Use a shared global stylesheet for consistent look and feel.
- Keep class names semantic and consistent across components.
