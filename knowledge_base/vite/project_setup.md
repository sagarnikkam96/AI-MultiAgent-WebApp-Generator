# Vite — Project Setup

Scaffolding and configuring the generated React + TypeScript project with Vite.

## Why Vite

Vite provides fast cold starts, instant hot module replacement (HMR), and a simple build
pipeline for React + TypeScript apps.

## Typical scaffold

A Vite React-TS project contains:

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── main.tsx          # React entrypoint / mount
    ├── App.tsx           # Root component
    └── ...
```

## Key `package.json` scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }
}
```

- `dev` — local dev server with HMR.
- `build` — type-check with `tsc` then bundle with Vite.
- `preview` — serve the production build locally.

## Entry point

`index.html` references `/src/main.tsx`, which mounts the React root:

```tsx
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

## Dev proxy

Use Vite's dev server proxy to forward API calls to the backend so the frontend stays
same-origin (avoids CORS). See `vite.config.ts` `server.proxy`.
