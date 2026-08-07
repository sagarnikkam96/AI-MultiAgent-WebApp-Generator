import { useState } from 'react';

type Doctor = {
  id: number;
  name: string;
  specialty: string;
};

const HospitalManagementSystem: React.FC = () => {
  const [doctors, setDoctors] = useState<Doctor[]>([
    { id: 1, name: 'John Doe', specialty: 'Cardiology' },
    { id: 2, name: 'Jane Smith', specialty: 'Orthopedics' },
    { id: 3, name: 'Sam Brown', specialty: 'Dermatology' },
  ]);

  return (
    <div className="container">
      <h1>Doctor Management System</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Specialty</th>
          </tr>
        </thead>
        <tbody>
          {doctors.map((doctor) => (
            <tr key={doctor.id}>
              <td>{doctor.id}</td>
              <td>{doctor.name}</td>
              <td>{doctor.specialty}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default HospitalManagementSystem;