import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

// Importing child components
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import Patients from "./components/Patients";
import Doctors from "./components/Doctors";

const HospitalManagementSystem: React.FC = () => {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={Login} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/patients" component={Patients} />
        <Route path="/doctors" component={Doctors} />
      </Switch>
    </Router>
  );
};

export default HospitalManagementSystem;