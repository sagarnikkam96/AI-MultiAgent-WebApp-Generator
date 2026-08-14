# React — Components

Core component concepts for the generated React + TypeScript frontend.

## Component model

- Components are functions that receive `props` and return JSX/React elements.
- Prefer function components over classes.
- Name components with `PascalCase`; files usually match the component name.

```tsx
interface CardProps {
  title: string;
  children?: React.ReactNode;
}

export function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  );
}
```

## Composition over inheritance

- Build small, focused components and compose them into larger screens.
- Lift shared state to a common parent and pass data/handlers down via props.
- Keep presentational components as pure as possible (props in, JSX out).

## Props and immutability

- Treat props as read-only; never mutate them.
- React re-renders when props or state change; keep prop types explicit with interfaces.
- Use TypeScript interfaces to define the props contract of every component.

## Keys in lists

- Always give list items a stable, unique `key` (e.g. a database id) to keep reconciliation
  correct and avoid rendering bugs.

```tsx
<ul>
  {items.map((item) => (
    <li key={item.id}>{item.name}</li>
  ))}
</ul>
```

## Styling

- Use CSS classes imported in the component, or a single global stylesheet for the app.
- Keep class names semantic and consistent (e.g. `kebab-case`).
