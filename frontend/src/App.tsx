import { useEffect, useState } from 'react';
import { analyzeProject, getBackendStatus } from './services/api';

type BackendStatus = {
  message: string;
  status: string;
  version: string;
};

type RequirementAnalysis = {
  project_name: string;
  project_type: string;
  frontend: string;
  backend: string;
  database: string;
  authentication: boolean;
  modules: string[];
  validation_errors: string[];
};

function App() {
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [analysis, setAnalysis] = useState<RequirementAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

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

  const handleAnalyze = async () => {
    if (!prompt.trim()) {
      setAnalysisError('Please enter a project prompt.');
      return;
    }

    setAnalyzing(true);
    setAnalysisError(null);
    setAnalysis(null);

    try {
      const result = await analyzeProject(prompt);
      setAnalysis(result);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Failed to analyze project');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <main style={{ fontFamily: 'sans-serif', padding: '2rem', maxWidth: '700px', margin: '0 auto' }}>
      <h1>Backend Status</h1>

      {loading && <p>Loading...</p>}

      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {status && (
        <div style={{ marginBottom: '2rem' }}>
          <p><strong>Message:</strong> {status.message}</p>
          <p><strong>Status:</strong> {status.status}</p>
          <p><strong>Version:</strong> {status.version}</p>
        </div>
      )}

      <h2>Project Analysis</h2>
      <textarea
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        placeholder="Describe your project requirements"
        rows={6}
        style={{ width: '100%', padding: '0.75rem', marginBottom: '1rem' }}
      />

      <button onClick={handleAnalyze} disabled={analyzing} style={{ padding: '0.6rem 1rem' }}>
        {analyzing ? 'Generating...' : 'Generate'}
      </button>

      {analysisError && <p style={{ color: 'crimson', marginTop: '1rem' }}>{analysisError}</p>}

      {analysis && (
        <div style={{ marginTop: '1.5rem' }}>
          <p><strong>Project Name:</strong> {analysis.project_name}</p>
          <p><strong>Project Type:</strong> {analysis.project_type}</p>
          <p><strong>Frontend:</strong> {analysis.frontend}</p>
          <p><strong>Backend:</strong> {analysis.backend}</p>
          <p><strong>Database:</strong> {analysis.database}</p>
          <p><strong>Authentication:</strong> {analysis.authentication ? 'Yes' : 'No'}</p>
          <p><strong>Modules:</strong> {analysis.modules.join(', ') || 'None'}</p>
          <p><strong>Validation Errors:</strong> {analysis.validation_errors.length > 0 ? analysis.validation_errors.join(', ') : 'None'}</p>
        </div>
      )}
    </main>
  );
}

export default App;
