import React from "react";

interface Patient {
  id: number;
  name: string;
  age: number;
}

const PatientManagementPage = () => {
  const patients: Patient[] = [
    { id: 1, name: "John Doe", age: 30 },
    { id: 2, name: "Jane Smith", age: 25 },
    // Add more patient records here
  ];

  return (
    <div>
      <h1>Patient Management</h1>
      <ul>
        {patients.map((patient) => (
          <li key={patient.id}>
            {patient.name}, {patient.age} years old
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PatientManagementPage;