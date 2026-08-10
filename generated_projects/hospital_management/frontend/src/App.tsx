import React from 'react';
import Login from './Login';
import Dashboard from './Dashboard';
import SectionOne from './SectionOne';
import SectionTwo from './SectionTwo';

const App: React.FC = () => {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">Hospital Management System</div>
        <nav className="nav-list">
          <a href="#dashboard" className="active">Dashboard</a>
          <a href="#section-1">Patients</a>
          <a href="#section-2">Doctors</a>
          <a href="#quick-access">Quick Access</a>
        </nav>
      </aside>
      <main className="page-content">
        <header className="topbar">
          <h1>Hospital Management System</h1>
          <div className="top-actions">
            <button type="button">Create New</button>
            <button type="button">Insights</button>
          </div>
        </header>

        <section id="dashboard" className="content-block">
          <Dashboard />
        </section>

        <section id="section-1" className="content-block grid-block">
          <div>
            <SectionOne />
          </div>
          <div>
            <SectionTwo />
          </div>
        </section>

        <section id="quick-access" className="content-block">
          <div className="panel">
            <h2>Quick Access</h2>
            <Login />
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;
