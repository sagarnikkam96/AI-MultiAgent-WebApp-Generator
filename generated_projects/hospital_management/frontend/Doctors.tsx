Certainly! Below is a combined source code for a simple doctor management page in a React frontend application using TypeScript and Vite:

// src/App.tsx

import React from 'react';
import './App.css';

interface Doctor {
  id: number;
  name: string;
  department: string;
}

const doctors: Doctor[] = [
  { id: 1, name: 'Dr. John Doe', department: 'Cardiology' },
  { id: 2, name: 'Dr. Jane Smith', department: 'Orthopedics' },
  { id: 3, name: 'Dr. Sarah Johnson', department: 'Pediatrics' }
];

const DoctorList: React.FC = () => {
  return (
    <div className="doctor-list">
      <h1>Doctor Management</h1>
      <ul>
        {doctors.map((doctor) => (
          <li key={doctor.id}>
            <strong>{doctor.name}</strong> - {doctor.department}
          </li>
        ))}
      </ul>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <DoctorList />
      </header>
    </div>
  );
}

export default App;

```css
/* src/App.css */

.App {
  font-family: Arial, sans-serif;
  text-align: center;
  margin-top: 50px;
}

.doctor-list ul {
  list-style-type: none;
  padding: 0;
}

.doctor-list li {
  border-bottom: 1px solid #ccc;
  padding: 10px 0;
}

This code sets up a basic React application with a `DoctorList` component that displays a list of doctors. The main `App` component renders the `DoctorList` within its header section. The styles are defined in `App.css` for simplicity and clarity.