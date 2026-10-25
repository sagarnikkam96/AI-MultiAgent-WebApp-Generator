import React, { useState } from 'react';

const FormEntry: React.FC = () => {
  const [name, setName] = useState('');
  const [status, setStatus] = useState('');
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Placeholder: just reset fields
    setName('');
    setStatus('');
    alert('Form submitted (placeholder)');
  };
  return (
    <div className="card">
      <h3 className="card-title">📝 Add Entry Form</h3>
      <form onSubmit={handleSubmit} className="row">
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="prompt-input"
          required
        />
        <input
          type="text"
          placeholder="Status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="prompt-input"
          required
        />
        <button type="submit" className="btn btn-primary btn-sm">Add</button>
      </form>
    </div>
  );
};

export default FormEntry;
