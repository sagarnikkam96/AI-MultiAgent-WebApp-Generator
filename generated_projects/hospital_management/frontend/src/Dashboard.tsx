import React from 'react';
import { Card } from '@mui/material';

interface HospitalDashboardProps {
  patientCount: number;
  doctorCount: number;
  appointmentCount: number;
}

const HospitalDashboard: React.FC<HospitalDashboardProps> = ({ patientCount, doctorCount, appointmentCount }) => (
  <div>
    <Card sx={{ margin: '20px' }}>
      <h2>Patient Summary</h2>
      <p>Total Patients: {patientCount}</p>
    </Card>

    <Card sx={{ margin: '20px' }}>
      <h2>Doctor Summary</h2>
      <p>Total Doctors: {doctorCount}</p>
    </Card>

    <Card sx={{ margin: '20px' }}>
      <h2>Appointment Summary</h2>
      <p>Total Appointments: {appointmentCount}</p>
    </Card>
  </div>
);

export default HospitalDashboard;