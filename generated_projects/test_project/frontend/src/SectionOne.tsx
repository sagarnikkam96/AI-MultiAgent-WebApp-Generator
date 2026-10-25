import React from 'react';

const SectionOne: React.FC = () => {
  const items = [
    { id: 1, label: 'Example Item', detail: 'Active' },
    { id: 2, label: 'Second Item', detail: 'Pending' },
    { id: 3, label: 'Third Item', detail: 'Ready' },
  ];

  return (
    <div className="resource-card">
      <h2>SectionOne</h2>
      <ul className="resource-list">
        {items.map((item) => (
          <li key={item.id}>
            <strong>{item.label}</strong> — {item.detail}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SectionOne;
