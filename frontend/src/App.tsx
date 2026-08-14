import { useEffect, useState } from 'react';
import {
  analyzeProject,
  getBackendStatus,
  buildProject,
  getProjectStatus,
  downloadProjectZipUrl,
  projectPreviewUrl,
  type GeneratedProjectResponse,
  type BuildProjectResponse,
  type ProjectStatusResponse,
} from './services/api';

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
  generated_project?: GeneratedProjectResponse | null;
};

function App() {
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [projectStatus, setProjectStatus] = useState<ProjectStatusResponse | null>(null);
  const [buildResult, setBuildResult] = useState<BuildProjectResponse | null>(null);
  const [building, setBuilding] = useState(false);
  const [buildMessage, setBuildMessage] = useState<string | null>(null);

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
      setBuildResult(null);
      setBuildMessage(null);
      setProjectStatus(null);

      const slug = result.generated_project?.project_slug;
      if (slug) {
        try {
          setProjectStatus(await getProjectStatus(slug));
        } catch {
          setProjectStatus(null);
        }
      }
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Failed to analyze project');
    } finally {
      setAnalyzing(false);
    }
  };

  const generatedProject = analysis?.generated_project;
  const projectSlug = generatedProject?.project_slug ?? null;
  const previewLink = projectSlug ? projectPreviewUrl(projectSlug) : null;

  const handleBuild = async () => {
    if (!projectSlug) return;
    setBuilding(true);
    setBuildMessage('Installing dependencies and building the frontend...');
    setBuildResult(null);
    try {
      const result = await buildProject(projectSlug);
      setBuildResult(result);
      setBuildMessage(
        result.built
          ? 'Build successful! Your website is ready to preview.'
          : 'Build did not produce a runnable site. See the logs below.'
      );
      try {
        setProjectStatus(await getProjectStatus(projectSlug));
      } catch {
        setProjectStatus(null);
      }
    } catch (err) {
      setBuildMessage(err instanceof Error ? err.message : 'Build failed');
    } finally {
      setBuilding(false);
    }
  };

  const handleDownload = () => {
    if (!projectSlug) return;
    window.open(downloadProjectZipUrl(projectSlug), '_blank');
  };

  const handlePreview = () => {
    if (previewLink) {
      window.open(previewLink, '_blank');
    }
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <span className="hero-badge">✦ AI Multi-Agent Engine</span>
        <h1 className="hero-title">Web App Generator</h1>
        <p className="hero-subtitle">
          Describe an app in plain English — the multi-agent pipeline builds the React
          frontend, FastAPI backend, and database schema for you.
        </p>

        <div className="status-pill-wrap">
          {loading && <span className="status-pill loading">Checking backend…</span>}
          {error && <span className="status-pill error">⚠ {error}</span>}
          {status && (
            <span className="status-pill ok">
              ● {status.status === 'success' ? 'Backend online' : status.status} · v{status.version}
            </span>
          )}
        </div>
      </header>

      <section className="card">
        <h2 className="card-title"><span className="emoji">📝</span> Project Analysis</h2>
        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Describe your project requirements..."
          rows={6}
          className="prompt-input"
        />
        <div className="row">
          <button onClick={handleAnalyze} disabled={analyzing} className="btn btn-primary btn-lg">
            {analyzing ? '✦ Generating…' : '⚡ Generate'}
          </button>
          <span className="hint">e.g. “Build a hospital management system with appointment booking”</span>
        </div>

        {analysisError && <p className="alert alert-error">{analysisError}</p>}

      {analysis && (
        <div className="results">
          <div className="result-grid">
            <div className="stat"><span className="stat-label">Project Name</span><span className="stat-value">{analysis.requirements.project_name}</span></div>
            <div className="stat"><span className="stat-label">Project Type</span><span className="stat-value">{analysis.requirements.project_type}</span></div>
            <div className="stat"><span className="stat-label">Frontend</span><span className="stat-value">{analysis.requirements.frontend}</span></div>
            <div className="stat"><span className="stat-label">Backend</span><span className="stat-value">{analysis.requirements.backend}</span></div>
            <div className="stat"><span className="stat-label">Database</span><span className="stat-value">{analysis.requirements.database}</span></div>
            <div className="stat"><span className="stat-label">Authentication</span><span className="stat-value">{analysis.requirements.authentication ? '✅ Yes' : '➖ No'}</span></div>
          </div>

          <div className="chip-row">
            <span className="chip-label">Modules:</span>
            {analysis.requirements.modules.length > 0 ? (
              analysis.requirements.modules.map((m) => <span key={m} className="chip">{m}</span>)
            ) : (
              <span className="stat-value">None</span>
            )}
          </div>

          {analysis.requirements.validation_errors.length > 0 && (
            <p className="alert alert-error">
              <strong>Validation errors:</strong> {analysis.requirements.validation_errors.join(', ')}
            </p>
          )}

          <section className="card inner">
            <h3 className="card-title">✨ AI Generated Project Summary</h3>
            <div className="ai-summary">
              {analysis.ollama_response ? analysis.ollama_response : 'No AI response available.'}
            </div>
          </section>

          <section className="card inner">
            <h3 className="card-title">🛠 Generated Website</h3>

            {generatedProject?.error ? (
              <p className="alert alert-error"><strong>Project generation failed:</strong> {generatedProject.error}</p>
            ) : (
              <>
                <div className="result-grid">
                  <div className="stat"><span className="stat-label">Project folder</span><span className="stat-value">{generatedProject?.project_path ? `backend/${generatedProject.project_path}` : 'Unknown'}</span></div>
                  <div className="stat"><span className="stat-label">Files created</span><span className="stat-value">{generatedProject?.files_count ?? 0}</span></div>
                  <div className="stat"><span className="stat-label">Status</span>
                    <span className="stat-value">
                      {projectStatus?.built
                        ? '✅ Built & ready to preview'
                        : projectStatus?.frontend
                        ? 'Generated (not built yet)'
                        : 'Generated'}
                    </span>
                  </div>
                </div>

                <div className="btn-row">
                  <button
                    onClick={handleBuild}
                    disabled={building || !projectSlug}
                    className="btn btn-green"
                  >
                    {building ? '⏳ Building…' : '🛠 Build & Preview'}
                  </button>

                  {projectStatus?.built && (
                    <button onClick={handlePreview} className="btn btn-blue">▶ Open Preview</button>
                  )}

                  <button onClick={handleDownload} disabled={!projectSlug} className="btn btn-purple">
                    ⬇ Download ZIP
                  </button>
                </div>

                {buildMessage && (
                  <div className="alert alert-info"><strong>{buildMessage}</strong></div>
                )}

                {buildResult?.build_success && (
                  <p className="alert alert-success">
                    ✅ Your website is live. Click{' '}
                    <a href={previewLink ?? '#'} target="_blank" rel="noreferrer">Open Preview</a>{' '}
                    to view it in a new tab.
                  </p>
                )}

                {buildResult && (
                  <details className="log-block">
                    <summary>Build logs</summary>
                    <pre className="log-pre">
                      {buildResult.install_log || 'No install log'}
                      {'\n\n--- BUILD ---\n\n'}
                      {buildResult.build_log || 'No build log'}
                    </pre>
                  </details>
                )}

                {generatedProject?.files_created && generatedProject.files_created.length > 0 && (
                  <details className="log-block">
                    <summary>
                      Generated files ({generatedProject.files_created.length})
                    </summary>
                    <ul className="file-list">
                      {generatedProject.files_created.map((file) => (
                        <li key={file}>{file}</li>
                      ))}
                    </ul>
                  </details>
                )}
              </>
            )}
          </section>
        </div>
      )}
      </section>
    </main>
  );
}

export default App;
