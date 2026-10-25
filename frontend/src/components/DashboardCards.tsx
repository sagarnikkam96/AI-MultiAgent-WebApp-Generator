import React, { useEffect, useState } from 'react';

type DashboardData = {
  total_patients: number;
  appointments_today: number;
  available_beds: number;
};

const DashboardCards: React.FC = () => {
  const [data, setData] = useState<DashboardData>({
    total_patients: 0,
    appointments_today: 0,
    available_beds: 0,
  });

  useEffect(() => {
    fetch('/api/dashboard/counts')
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch((err) => console.error('Failed to fetch dashboard counts', err));
  }, []);

  const cards = [
    { title: 'Total Patients', value: data.total_patients },
    { title: 'Appointments Today', value: data.appointments_today },
    { title: 'Available Beds', value: data.available_beds },
  ];
  return (
    <div className="card">
      <h3 className="card-title">📊 Dashboard Overview</h3>
      <div className="result-grid">
        {cards.map((c) => (
          <div key={c.title} className="stat">
            <span className="stat-label">{c.title}</span>
            <span className="stat-value">{c.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DashboardCards;
