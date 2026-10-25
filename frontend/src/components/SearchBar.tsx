import React, { useState } from 'react';

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`Search for: ${query}`);
    setQuery('');
  };
  return (
    <div className="card">
      <h3 className="card-title">🔍 Search / Filter</h3>
      <form onSubmit={handleSearch} className="row">
        <input
          type="text"
          placeholder="Search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="prompt-input"
        />
        <button type="submit" className="btn btn-primary btn-sm">Search</button>
      </form>
    </div>
  );
};

export default SearchBar;
