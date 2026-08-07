// src/main.tsx
import { createRoot } from 'react-dom/client';
import App from './App';

const container = document.getElementById('root')!;
if (!container) throw new Error('Failed to find the root element');

const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// src/App.tsx
import React from 'react';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Welcome to the Hospital Management System</h1>
      </header>
      <main className="app-main">
        {/* Main content of the application */}
      </main>
      <footer className="app-footer">
        <p>&copy; 2023 Hospital Management System. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;

```css
/* src/App.css */
.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;
}

.app-header, .app-footer {
  background-color: #333;
  color: white;
  padding: 1rem;
  width: 100%;
  text-align: center;
}

.app-main {
  flex-grow: 1;
  padding: 2rem;
}

```json
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../dist',
  },
});

This source code provides a basic structure for a React + TypeScript application named "Hospital Management System". It includes the main entry point (`main.tsx`), a simple `App` component (`App.tsx`), and CSS styling (`App.css`). The Vite configuration file is also provided to set up the build process.