import { useState } from 'react';

interface Doctor {
  id: number;
  name: string;
}

const Doctors = () => {
  const [doctors, setDoctors] = useState<Doctor[]>([
    { id: 1, name: 'Dr. John Doe' },
    { id: 2, name: 'Dr. Jane Smith' },
    // Add more doctors as needed
  ]);

  const addDoctor = (name: string) => {
    const newDoctor: Doctor = { id: doctors.length + 1, name };
    setDoctors([...doctors, newDoctor]);
  };

  return (
    <div>
      <h1>Doctor Management</h1>
      <form onSubmit={(e) => e.preventDefault()}>
        <input
          type="text"
          placeholder="Add a doctor's name"
          onChange={(e) =>
            setDoctors((prevDocters) =>
              prevDocters.map(doctor =>
                doctor.id === 0 ? { ...doctor, name: e.target.value } : doctor
              )
            )
          }
        />
        <button type="submit">Add Doctor</button>
      </form>
      <ul>
        {doctors.map((doctor) => (
          <li key={doctor.id}>
            {doctor.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Doctors;