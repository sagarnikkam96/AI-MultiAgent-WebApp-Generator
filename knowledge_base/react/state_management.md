# React — State Management

Managing local and shared state in a React + TypeScript frontend.

## Local component state

Use the `useState` hook for state owned by a single component:

```tsx
const [count, setCount] = useState<number>(0);
```

- Only read `state` during render; update it via the setter.
- When the new value depends on the previous one, use the functional form:
  `setCount((prev) => prev + 1)`.

## Effects

Use `useEffect` for side effects (fetching data, subscriptions, timers):

```tsx
useEffect(() => {
  let cancelled = false;
  fetchData().then((data) => {
    if (!cancelled) setData(data);
  });
  return () => {
    cancelled = true;
  };
}, [/* deps */]);
```

- Always specify the dependency array; clean up subscriptions/async in the returned function.

## Lifting state up

When multiple components need the same data:
- Move the state to the nearest common ancestor.
- Pass values and update callbacks down through props.

## Context (optional)

Use React Context sparingly for app-wide data (e.g. authenticated user, theme). Avoid
overusing context for frequently-changing values that would re-render large subtrees.

## Async data & loading

- Keep loading / error / data states explicit (e.g. `loading`, `error`, `data`).
- Render clear loading indicators and error messages to the user.

## Rule of thumb

Start with local `useState`; only introduce more elaborate state management when prop
drilling or cross-component sharing becomes painful. Keep the generated frontend simple.
