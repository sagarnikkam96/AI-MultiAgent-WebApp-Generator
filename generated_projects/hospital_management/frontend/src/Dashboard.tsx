import { useState } from 'react';
import axios from 'axios';

interface HospitalSummary {
  name: string;
  patientsCount: number;
  bedsAvailable: number;
}

const HospitalDashboard = () => {
  const [summary, setSummary] = useState<HospitalSummary | null>(null);

  useEffect(() => {
    axios.get('/api/hospital-summary')
      .then(response => {
        setSummary(response.data);
      })
      .catch(error => {
        console.error('Error fetching hospital summary:', error);
      });
  }, []);

  return (
    <div className="dashboard">
      {summary ? (
        <>
          <h1>Hospital Management System</h1>
          <div className="summary-cards">
            <div className="card">
              <h2>Name: {summary.name}</h2>
              <p>Patients Count: {summary.patientsCount}</p>
              <p>Beds Available: {summary.bedsAvailable}</p>
            </div>
            {/* Add more cards as needed */}
          </div>
        </>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default HospitalDashboard;