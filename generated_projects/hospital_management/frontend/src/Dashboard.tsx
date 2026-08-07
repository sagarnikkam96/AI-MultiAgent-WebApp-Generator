import React from 'react';
import { Card } from 'antd';

const HospitalDashboardPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Summary Cards */}
      <Card title="Patients">
        <p>10,500 registered</p>
      </Card>
      <Card title="Doctors">
        <p>80 available</p>
      </Card>
      <Card title="Appointments Today">
        <p>250 pending</p>
      </Card>
    </div>
  );
};

export default HospitalDashboardPage;