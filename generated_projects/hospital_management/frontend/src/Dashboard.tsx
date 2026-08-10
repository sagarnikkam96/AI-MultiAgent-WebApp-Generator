import React from 'react';

const Dashboard: React.FC = () => {
  const stats = [
    { label: 'Total Patients', value: '1,280' },
    { label: 'Active Doctors', value: '72' },
    { label: 'Open Appointments', value: '34' },
    { label: 'Available Beds', value: '18' },
  ];

  return (
    <div className="dashboard-grid">
      {stats.map((stat, index) => (
        <div key={index} className="dashboard-card">
          <span className="stat-label">{stat.label}</span>
          <strong>{stat.value}</strong>
        </div>
      ))}
    </div>
  );
};

export default Dashboard;
