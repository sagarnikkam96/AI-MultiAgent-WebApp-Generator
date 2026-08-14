# Vite — Build

Building and serving the generated frontend with Vite.

## Production build

Run `npm run build` (i.e. `tsc && vite build`). This:
1. Type-checks the TypeScript (`tsc`).
2. Bundles the app and outputs static assets to `dist/`.

Output includes `dist/index.html` plus hashed assets under `dist/assets/`.

## Base path considerations

Vite's `base` option controls where assets are referenced. When the built site is served
from a sub-path (e.g. `/projects/{slug}/preview`), asset URLs must resolve correctly.
- Default `base: "/"` produces absolute `/assets/...` references.
- `base: "./"` produces relative `./assets/...` references.

The backend preview endpoint rewrites asset references so built sites render under their
preview mount point.

## Environment variables

- `import.meta.env.VITE_*` variables are inlined at build time.
- Use them for backend base URLs / proxy targets (e.g. `VITE_API_BASE_URL`,
  `VITE_PROXY_TARGET`).

## Previewing

- `npm run preview` serves the production build locally.
- In this project, the FastAPI backend serves the built site via
  `/projects/{slug}/preview`, with SPA fallback to `index.html`.

## Common build checks

- Ensure `dist/index.html` exists after a successful build.
- Verify assets resolve under the preview mount point (rewrite `/assets/` or `./assets/`).
- Keep `tsconfig` strict so `tsc` catches type issues before bundling.
