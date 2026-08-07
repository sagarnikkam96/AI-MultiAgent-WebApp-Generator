import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

// Import your component files here
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Patients from './components/Patients';
import Doctors from './components/Doctors';

const App: React.FC = () => {
  return (
    <Router>
      <Switch>
        <Route path="/login" exact component={Login} />
        <Route path="/" exact component={Dashboard} />
        <Route path="/patients" exact component={Patients} />
        <Route path="/doctors" exact component={Doctors} />
      </Switch>
    </Router>
  );
};

export default App;