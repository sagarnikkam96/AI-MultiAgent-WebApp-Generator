import React from 'react';

interface Doctor {
  id: number;
  name: string;
  specialization: string;
  email: string;
}

interface DoctorsPageProps {
  doctors: Doctor[];
}

const DoctorsPage: React.FC<DoctorsPageProps> = ({ doctors }) => {
  return (
    <div>
      <h1>Doctor Management</h1>
      <table border="1">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Specialization</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          {doctors.map((doctor) => (
            <tr key={doctor.id}>
              <td>{doctor.id}</td>
              <td>{doctor.name}</td>
              <td>{doctor.specialization}</td>
              <td>{doctor.email}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DoctorsPage;