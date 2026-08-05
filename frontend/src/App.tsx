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

type AnalysisResult = {
  requirements: RequirementAnalysis;
  project_plan: Record<string, unknown>;
  backend_blueprint: Record<string, unknown>;
  database_blueprint: Record<string, unknown>;
  ollama_response?: string | null;
};

function App() {
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
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
          <p><strong>Project Name:</strong> {analysis.requirements.project_name}</p>
          <p><strong>Project Type:</strong> {analysis.requirements.project_type}</p>
          <p><strong>Frontend:</strong> {analysis.requirements.frontend}</p>
          <p><strong>Backend:</strong> {analysis.requirements.backend}</p>
          <p><strong>Database:</strong> {analysis.requirements.database}</p>
          <p><strong>Authentication:</strong> {analysis.requirements.authentication ? 'Yes' : 'No'}</p>
          <p><strong>Modules:</strong> {analysis.requirements.modules.join(', ') || 'None'}</p>
          <p><strong>Validation Errors:</strong> {analysis.requirements.validation_errors.length > 0 ? analysis.requirements.validation_errors.join(', ') : 'None'}</p>

          <section style={{ marginTop: '1.5rem' }}>
            <h2>AI Generated Project Summary</h2>
            <div
              style={{
                padding: '1rem',
                borderRadius: '12px',
                border: '1px solid #ddd',
                backgroundColor: '#f9f9fb',
                whiteSpace: 'pre-wrap',
                minHeight: '4rem',
              }}
            >
              {analysis.ollama_response ? analysis.ollama_response : 'No AI response available.'}
            </div>
          </section>
        </div>
      )}
    </main>
  );
}

export default App;
