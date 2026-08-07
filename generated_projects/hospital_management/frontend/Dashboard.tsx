Certainly! Below is a simplified example of how you might structure the main React component for a "Hospital Management System" dashboard using React and TypeScript. This example will focus on creating a simple dashboard with summary cards.

// src/App.tsx

import React from 'react';
import { Box, Typography } from '@mui/material';

const HospitalDashboard = () => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', height: '100vh' }}>
      {/* Summary Card */}
      <Box
        p={2}
        bgcolor="primary.main"
        color="white"
        borderRadius={8}
        m={2}
        textAlign="center"
        width={300}
      >
        <Typography variant="h5">Summary</Typography>
        <Typography variant="subtitle1">Number of Patients: 500</Typography>
        <Typography variant="subtitle1">Available Beds: 30</Typography>
        {/* Add more summary statistics as needed */}
      </Box>

      {/* Another Summary Card */}
      <Box
        p={2}
        bgcolor="secondary.main"
        color="white"
        borderRadius={8}
        m={2}
        textAlign="center"
        width={300}
      >
        <Typography variant="h5">Staff Information</Typography>
        <Typography variant="subtitle1">Doctors: 40</Typography>
        <Typography variant="subtitle1">Nurses: 60</Typography>
        {/* Add more staff statistics as needed */}
      </Box>

      {/* More summary cards can be added here */}
    </Box>
  );
};

export default HospitalDashboard;

This code provides a basic structure for the dashboard with two summary cards. You can expand upon this by adding more components, fetching data from an API, or using state management libraries like React Context or Redux to manage your application's state.