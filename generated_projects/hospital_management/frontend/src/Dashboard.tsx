import React from 'react';
import type { AppRecord } from './App';

interface DashboardProps {
  records: AppRecord[];
  entityCounts?: Record<string, number>;
  databaseCountError?: string | null;
  countsSource: 'database' | 'browser';
}

const stats = [{"label": "Patients", "key": "patients"}, {"label": "Doctors", "key": "doctors"}, {"label": "Appointments", "key": "appointments"}, {"label": "Billing", "key": "billings"}];

const Dashboard: React.FC<DashboardProps> = ({ records, entityCounts, databaseCountError, countsSource }) => {
  return (
    <div className="dashboard-content">
      {databaseCountError && <p className="muted" role="status">Database counts are unavailable: {databaseCountError}</p>}
      <div className="dashboard-grid">
        {stats.map((stat) => (
          <article className="dashboard-card" key={stat.key}>
            <span className="stat-label">{stat.label}</span>
            <strong className="stat-value">{entityCounts?.[stat.key] ?? '—'}</strong>
            <span className="stat-sub">{countsSource === 'database' ? 'From the application database' : 'Saved in this browser'}</span>
          </article>
        ))}
      </div>

      <div className="dashboard-record-section recent-section">
        <div className="section-head-row">
          <div>
            <p className="eyebrow">Activity</p>
            <h2>Patients added recently</h2>
          </div>
          <span className="badge-pill">{records.length} in this session</span>
        </div>
        {records.length === 0 ? (
          <div className="empty-state">
            <span aria-hidden="true">+</span>
            <strong>No patients have been added yet.</strong>
            <p className="muted">Create your first record to start building this workspace.</p>
          </div>
        ) : (
          <ul className="resource-list recent-list">
            {records.slice(0, 4).map((r) => (
              <li key={r.id}>
                <span className="record-mark">{r.name.slice(0, 1).toUpperCase()}</span>
                <span>
                  <strong>{r.name}</strong> - {r.field2} - <small className="muted">{r.createdAt}</small>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
