// hospital-management-system/src/App.tsx

import { useState } from 'react';

interface Patient {
  id: number;
  name: string;
  age: number;
}

const App = () => {
  const [patients, setPatients] = useState<Patient[]>([]);

  const handleAddPatient = () => {
    const newPatient = {
      id: patients.length + 1,
      name: 'John Doe',
      age: Math.floor(Math.random() * 100) + 1,
    };
    setPatients([...patients, newPatient]);
  };

  return (
    <div className="App">
      <h1>Hospital Management System</h1>
      <button onClick={handleAddPatient}>Add Patient</button>
      <ul>
        {patients.map(patient => (
          <li key={patient.id}>
            {patient.name}, {patient.age} years old
          </li>
        ))}
      </ul>
    </div>
  );
};

export default App;