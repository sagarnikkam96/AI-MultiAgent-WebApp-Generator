import React from 'react';

interface Patient {
  id: number;
  name: string;
  age: number;
  symptoms: string[];
}

const PatientManagementPage: React.FC = () => {
  const [patients, setPatients] = React.useState<Patient[]>([
    { id: 1, name: "John Doe", age: 30, symptoms: ["Fever"] },
    { id: 2, name: "Jane Smith", age: 45, symptoms: ["Cough"] },
    { id: 3, name: "Emily Johnson", age: 60, symptoms: ["Headache"] },
  ]);

  return (
    <div>
      <h1>Patient Management System</h1>
      <ul>
        {patients.map((patient) => (
          <li key={patient.id}>
            <strong>{patient.name}</strong> - {patient.age}
            <ul>
              {patient.symptoms.map((symptom, index) => (
                <li key={index}>{symptom}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PatientManagementPage;