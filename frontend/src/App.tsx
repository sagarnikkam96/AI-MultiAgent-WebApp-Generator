import { useEffect, useState } from 'react';
import { getBackendStatus } from './services/api';

type BackendStatus = {
  message: string;
  status: string;
  version: string;
};

function App() {
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await getBackendStatus();
        setStatus(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load backend status');
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  return (
    <main style={{ fontFamily: 'sans-serif', padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Backend Status</h1>

      {loading && <p>Loading...</p>}

      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {status && (
        <div>
          <p><strong>Message:</strong> {status.message}</p>
          <p><strong>Status:</strong> {status.status}</p>
          <p><strong>Version:</strong> {status.version}</p>
        </div>
      )}
    </main>
  );
}

export default App;
