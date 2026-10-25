import React from 'react';

interface Row {
  id: number;
  name: string;
  status: string;
}

const mockData: Row[] = [
  { id: 1, name: 'John Doe', status: 'Admitted' },
  { id: 2, name: 'Jane Smith', status: 'Discharged' },
  { id: 3, name: 'Bob Johnson', status: 'Pending' },
];

const DataTable: React.FC = () => {
  return (
    <div className="card">
      <h3 className="card-title">📋 Data Table</h3>
      <table className="stat">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {mockData.map((row) => (
            <tr key={row.id}>
              <td>{row.id}</td>
              <td>{row.name}</td>
              <td>{row.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
