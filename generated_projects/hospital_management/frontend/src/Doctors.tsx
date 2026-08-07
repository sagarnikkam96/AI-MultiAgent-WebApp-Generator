import React from 'react';
import { useState } from 'react';
import { Doctor } from './Doctor'; // Assuming you have a Doctor model

interface DoctorManagementProps {}

const DoctorManagement: React.FC<DoctorManagementProps> = () => {
  const [doctors, setDoctors] = useState([
    { id: 1, name: 'Dr. John Doe', specialty: 'Cardiology' },
    { id: 2, name: 'Dr. Jane Smith', specialty: 'Pediatrics' },
    // Add more doctors as needed
  ]);

  return (
    <div>
      <h1>Doctor Management</h1>
      <ul>
        {doctors.map((doctor) => (
          <li key={doctor.id}>
            <Doctor doctor={doctor} />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DoctorManagement;