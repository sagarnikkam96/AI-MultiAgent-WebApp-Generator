// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Login from './Login';
import Dashboard from './Dashboard';
import Patients from './Patients';
import Doctors from './Doctors';

function App() {
  return (
    <Router>
      <div className="App">
        <nav>
          {/* Navigation links here */}
        </nav>
        <Switch>
          <Route path="/login" component={Login} />
          <Route path="/dashboard" component={Dashboard} />
          <Route path="/patients" component={Patients} />
          <Route path="/doctors" component={Doctors} />
          <Route path="/" exact component={() => <h1>Welcome to the Hospital Management System</h1>} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;

// src/Login.tsx
import React, { useState } from 'react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Logic to authenticate user
    console.log('Logging in with:', username, password);
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <br />
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <br />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;

// src/Dashboard.tsx
import React from 'react';

const Dashboard = () => {
  return (
    <div>
      <h2>Dashboard</h2>
      {/* Dashboard content here */}
    </div>
  );
};

export default Dashboard;

// src/Patients.tsx
import React from 'react';

const Patients = () => {
  return (
    <div>
      <h2>Patients</h2>
      {/* Patients data list or form here */}
    </div>
  );
};

export default Patients;

// src/Doctors.tsx
import React from 'react';

const Doctors = () => {
  return (
    <div>
      <h2>Doctors</h2>
      {/* Doctors data list or form here */}
    </div>
  );
};

export default Doctors;