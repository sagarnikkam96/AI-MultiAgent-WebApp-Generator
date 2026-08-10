import React from 'react';

interface Patient {
  id: number;
  name: string;
  age: number;
}

const Patients = () => {
  const [patients, setPatients] = React.useState<Patient[]>([]);
  const [newPatientName, setNewPatientName] = React.useState('');
  const [newPatientAge, setNewPatientAge] = React.useState('0');

  const handleAddPatient = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (newPatientName.trim() !== '' && newPatientAge.trim() !== '') {
      setPatients([...patients, { id: patients.length + 1, name: newPatientName, age: parseInt(newPatientAge) }]);
      setNewPatientName('');
      setNewPatientAge('0');
    }
  };

  return (
    <div>
      <h1>Patient Management System</h1>
      <form onSubmit={handleAddPatient}>
        <input
          type="text"
          placeholder="Name"
          value={newPatientName}
          onChange={(e) => setNewPatientName(e.target.value)}
        />
        <input
          type="number"
          placeholder="Age"
          value={newPatientAge}
          onChange={(e) => setNewPatientAge(e.target.value)}
        />
        <button type="submit">Add Patient</button>
      </form>
      <ul>
        {patients.map((patient) => (
          <li key={patient.id}>
            {patient.name} - {patient.age}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Patients;