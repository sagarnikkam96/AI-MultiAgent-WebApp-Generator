import React from 'react';
import { useState } from 'react';

const HospitalManagementSystem: React.FC = () => {
  const [patients, setPatients] = useState([
    { id: 1, name: 'John Doe', age: 30 },
    { id: 2, name: 'Jane Smith', age: 25 },
    // Add more patient data as needed
  ]);

  return (
    <div>
      <h1>Patient Management System</h1>
      <ul>
        {patients.map(patient => (
          <li key={patient.id}>
            {patient.name} - {patient.age}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HospitalManagementSystem;