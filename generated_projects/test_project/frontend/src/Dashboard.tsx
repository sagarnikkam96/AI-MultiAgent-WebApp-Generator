import React from 'react';
import type { AppRecord } from './App';

interface DashboardProps {
  records: AppRecord[];
}

const Dashboard: React.FC<DashboardProps> = ({ records }) => {
  const stats = [
    { label: 'Active users', value: '1,240' },
    { label: 'Task completion', value: '82%' },
    { label: 'Engagement', value: '5,300' },
    { label: 'Growth', value: '14%' },
  ];

  return (
    <>
      <div className="dashboard-grid">
        {stats.map((stat, index) => (
          <div key={index} className="dashboard-card">
            <span className="stat-label">{stat.label}</span>
            <strong>{stat.value}</strong>
          </div>
        ))}
      </div>

      <div className="dashboard-record-section">
        <h2>Recently created</h2>
        {records.length === 0 ? (
          <p className="muted">Nothing created yet — use the Create New button (sign in first).</p>
        ) : (
          <ul className="resource-list">
            {records.slice(0, 4).map((r) => (
              <li key={r.id}>
                <strong>{r.name}</strong> — {r.field2} · {r.createdAt}
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
};

export default Dashboard;
