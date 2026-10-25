// Requests are same-origin and proxied to the FastAPI backend by Vite (see
// vite.config.ts). Override with VITE_API_BASE_URL if needed, e.g.
//   VITE_API_BASE_URL=http://127.0.0.1:8000
const API_BASE_URL: string = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? (import.meta.env.MODE === 'production' ? 'http://127.0.0.1:8000' : '');

export interface RequirementAnalysisResponse {
  project_name: string;
  project_type: string;
  frontend: string;
  backend: string;
  database: string;
  authentication: boolean;
  modules: string[];
  validation_errors: string[];
  language: string;
  purpose?: string;
  domain?: string;
  user_roles?: string[];
  features?: string[];
  pages?: string[];
  functional_requirements?: string[];
  data_requirements?: string[];
  constraints?: string[];
}

export interface TestingCheck {
  name: string;
  category: string;
  passed: boolean;
  details: string;
}

export interface TestingReportResponse {
  is_valid: boolean;
  passed_count: number;
  failed_count: number;
  checks: TestingCheck[];
  errors: string[];
  logs: string;
}

export interface DebugFix {
  file_path: string;
  issue_type: string;
  root_cause: string;
  fix_description: string;
  applied: boolean;
}

export interface DebugReportResponse {
  attempts: number;
  succeeded: boolean;
  fixes: DebugFix[];
  message: string;
  remaining_blockers: string[];
}

export interface SecurityVulnerability {
  check_name: string;
  severity: string;
  description: string;
  file_path?: string;
  remediation?: string;
  remediated: boolean;
}

export interface SecurityReportResponse {
  is_secure: boolean;
  score: number;
  passed_checks: string[];
  vulnerabilities: SecurityVulnerability[];
  summary: string;
}

export interface DeploymentArtifact {
  filename: string;
  path: string;
  description: string;
}

export interface DeploymentReportResponse {
  ready: boolean;
  artifacts: DeploymentArtifact[];
  environment_variables: string[];
  instructions: string;
  status_message: string;
}

export interface AnalyzeProjectResponse {
  requirements: RequirementAnalysisResponse;
  project_plan: Record<string, unknown>;
  backend_blueprint: Record<string, unknown>;
  database_blueprint: Record<string, unknown>;
  ollama_response?: string | null;
  narration_script?: string | null;
  generated_project?: GeneratedProjectResponse;
  testing_report?: TestingReportResponse | null;
  debug_report?: DebugReportResponse | null;
  security_report?: SecurityReportResponse | null;
  deployment_report?: DeploymentReportResponse | null;
  language: string;
}

export interface SDLCStatementOfWork {
  project_name: string;
  purpose: string;
  scope: string[];
  stakeholders: string[];
  functional_requirements: string[];
  non_functional_requirements: string[];
  data_requirements: string[];
  acceptance_criteria: string[];
}

export interface SDLCProjectDesign {
  system_architecture?: string;
  frontend_architecture?: string[];
  backend_architecture?: string[];
  database_architecture?: string[];
  apis?: string[];
}

export interface SDLCBackendDesign {
  framework?: string;
  authentication?: string;
  endpoints?: Array<{
    method: string;
    path: string;
    description: string;
    request_schema?: string | null;
    response_schema: string;
  }>;
  schemas?: string[];
}

export interface SDLCDatabaseDesign {
  database_type?: string;
  tables?: string[];
  relationships?: string[];
  indexes?: string[];
  table_details?: Array<{
    name: string;
    model_name: string;
    columns: Array<{
      name: string;
      data_type: string;
      primary_key: boolean;
      nullable: boolean;
      unique: boolean;
    }>;
    foreign_keys: string[];
  }>;
}

export interface SDLCPlanResponse {
  srs: SDLCStatementOfWork;
  requirements: RequirementAnalysisResponse;
  project_plan: SDLCProjectDesign;
  backend_blueprint: SDLCBackendDesign;
  database_blueprint: SDLCDatabaseDesign;
}

export interface GeneratedProjectResponse {
  project_name: string;
  project_slug?: string | null;
  project_path?: string | null;
  files_created: string[];
  files_count: number;
  error?: string;
}

export interface ProjectStatusResponse {
  slug: string;
  exists: boolean;
  frontend: boolean;
  backend: boolean;
  dist: boolean;
  built: boolean;
  file_count: number;
  frontend_file_count: number;
  backend_file_count: number;
}

export type PremiumDesignPersonality =
  | 'auto'
  | 'futuristic'
  | 'luxury'
  | 'cinematic'
  | 'creative'
  | 'editorial'
  | 'organic'
  | 'minimalist'
  | 'glassmorphism'
  | 'bold';

export interface PremiumDesignDirection {
  personality: Exclude<PremiumDesignPersonality, 'auto'>;
  source: 'local_model' | 'prompt_rules' | 'user_selected';
  fallback_reason: string | null;
  rationale: string;
  palette: Record<string, string>;
  typography: string;
  layout_direction: string;
  imagery_direction: string;
  motion_direction: string;
  accessibility: string[];
}

export interface PremiumDesignPreviewResponse {
  preview_id: string;
  project_slug: string;
  preview_url: string;
  direction: PremiumDesignDirection;
  validation: {
    passed: boolean;
    checks: string[];
  };
}

export interface PremiumDesignAcceptanceResponse {
  accepted: boolean;
  project_slug: string;
  personality: string;
  functional_validation: TestingReportResponse;
  message: string;
}

export interface BuildProjectResponse {
  slug: string;
  status: 'queued' | 'installing' | 'building' | 'completed' | 'failed';
  phase: string;
  install_success: boolean;
  build_success: boolean;
  built: boolean;
  install_log: string;
  build_log: string;
}

export interface GeneratedWebsite {
  project_slug: string;
  project_name: string;
  created_at: number;
  built: boolean;
}

export interface GeneratedWebsitesResponse {
  projects: GeneratedWebsite[];
  count: number;
}

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('generator_auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch (err) {
    // If relative proxy fetch failed, try direct backend URL http://127.0.0.1:8000
    if (!API_BASE_URL && typeof window !== 'undefined') {
      try {
        response = await fetch(`http://127.0.0.1:8000${path}`, init);
      } catch {
        throw new Error(
          'Could not connect to the backend server. Please make sure the backend is running on http://127.0.0.1:8000 (Run: python run_app.py or start.bat in VS Code).'
        );
      }
    } else {
      throw new Error(
        'Could not connect to the backend server. Please make sure the backend is running on http://127.0.0.1:8000.'
      );
    }
  }

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore
    }
    if (response.status === 404 && path.startsWith('/api/auth/')) {
      errorDetail =
        'The connected backend does not provide generator authentication. Start the main backend from the backend directory with: python -m uvicorn app.main:app --reload --port 8000.';
    }
    throw new Error(errorDetail);
  }

  return response.json() as Promise<T>;
}

export async function getBackendStatus(): Promise<{ message: string; status: string; version: string }> {
  try {
    return await request<{ message: string; status: string; version: string }>('/health');
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch backend status: ${error.message}`);
    }

    throw new Error('Failed to fetch backend status');
  }
}

export async function analyzeProject(userPrompt: string, language: string = "en"): Promise<AnalyzeProjectResponse> {
  try {
    return await request<AnalyzeProjectResponse>('/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify({ user_prompt: userPrompt, language }),
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to analyze project: ${error.message}`);
    }

    throw new Error('Failed to analyze project');
  }
}

export async function planSDLC(userPrompt: string, language: string = 'en'): Promise<SDLCPlanResponse> {
  try {
    return await request<SDLCPlanResponse>('/api/sdlc/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ user_prompt: userPrompt, language }),
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to plan SDLC workflow: ${error.message}`);
    }
    throw new Error('Failed to plan SDLC workflow');
  }
}

export async function generateApprovedSDLC(
  userPrompt: string,
  language: string,
  plan: SDLCPlanResponse,
): Promise<AnalyzeProjectResponse> {
  try {
    return await request<AnalyzeProjectResponse>('/api/sdlc/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({
        user_prompt: userPrompt,
        language,
        approved: true,
        requirements: plan.requirements,
        project_plan: plan.project_plan,
        backend_blueprint: plan.backend_blueprint,
        database_blueprint: plan.database_blueprint,
      }),
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to generate from approved design: ${error.message}`);
    }
    throw new Error('Failed to generate from approved design');
  }
}

export interface MultimodalAttachment {
  filename: string;
  kind: string;
  extracted: string;
  note: string;
}

export interface MultimodalAnalyzeResponse extends AnalyzeProjectResponse {
  multimodal?: { attachments: MultimodalAttachment[] };
}

export async function analyzeMultimodal(
  userPrompt: string,
  files: File[],
  language: string = "en",
): Promise<MultimodalAnalyzeResponse> {
  try {
    const formData = new FormData();
    formData.append('text', userPrompt);
    formData.append('language', language);
    for (const file of files) {
      formData.append('files', file, file.name);
    }

    return await request<MultimodalAnalyzeResponse>('/api/multimodal/analyze', {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to analyze multimodal input: ${error.message}`);
    }

    throw new Error('Failed to analyze multimodal input');
  }
}

export function downloadProjectZipUrl(projectSlug: string): string {
  return `${API_BASE_URL}/projects/${encodeURIComponent(projectSlug)}/download`;
}

export function projectFileUrl(projectSlug: string, filePath: string): string {
  const encodedPath = filePath.split('/').map((segment) => encodeURIComponent(segment)).join('/');
  return `${API_BASE_URL}/projects/${encodeURIComponent(projectSlug)}/files/${encodedPath}`;
}

export function projectPreviewUrl(projectSlug: string): string {
  return `${API_BASE_URL}/projects/${encodeURIComponent(projectSlug)}/preview`;
}

export async function getGeneratedWebsites(): Promise<GeneratedWebsitesResponse> {
  return await request<GeneratedWebsitesResponse>('/api/projects/history', {
    headers: authHeaders(),
  });
}

export async function getProjectStatus(projectSlug: string): Promise<ProjectStatusResponse> {
  try {
    return await request<ProjectStatusResponse>(`/projects/${encodeURIComponent(projectSlug)}`);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load project status: ${error.message}`);
    }

    throw new Error('Failed to load project status');
  }
}

export async function createPremiumDesignPreview(
  projectSlug: string,
  userPrompt: string,
  style: PremiumDesignPersonality = 'auto',
): Promise<PremiumDesignPreviewResponse> {
  try {
    return await request<PremiumDesignPreviewResponse>(
      `/projects/${encodeURIComponent(projectSlug)}/premium-design/preview`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ user_prompt: userPrompt, style }),
      },
    );
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to create premium design preview: ${error.message}`);
    }
    throw new Error('Failed to create premium design preview');
  }
}

export function premiumDesignPreviewUrl(projectSlug: string, previewId: string): string {
  return `${API_BASE_URL}/projects/${encodeURIComponent(projectSlug)}/premium-preview/${encodeURIComponent(previewId)}`;
}

export async function acceptPremiumDesign(
  projectSlug: string,
  previewId: string,
): Promise<PremiumDesignAcceptanceResponse> {
  try {
    return await request<PremiumDesignAcceptanceResponse>(
      `/projects/${encodeURIComponent(projectSlug)}/premium-design/${encodeURIComponent(previewId)}/accept`,
      { method: 'POST', headers: authHeaders() },
    );
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to apply premium design: ${error.message}`);
    }
    throw new Error('Failed to apply premium design');
  }
}

export async function rejectPremiumDesign(projectSlug: string, previewId: string): Promise<void> {
  try {
    await request<{ rejected: boolean }>(
      `/projects/${encodeURIComponent(projectSlug)}/premium-design/${encodeURIComponent(previewId)}`,
      { method: 'DELETE', headers: authHeaders() },
    );
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to discard premium design preview: ${error.message}`);
    }
    throw new Error('Failed to discard premium design preview');
  }
}

export async function testProject(projectSlug: string): Promise<TestingReportResponse> {
  try {
    return await request<TestingReportResponse>(`/projects/${encodeURIComponent(projectSlug)}/test`);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to test project: ${error.message}`);
    }
    throw new Error('Failed to test project');
  }
}

export async function debugProject(projectSlug: string): Promise<{ testing_report: TestingReportResponse; debug_report: DebugReportResponse }> {
  try {
    return await request<{ testing_report: TestingReportResponse; debug_report: DebugReportResponse }>(
      `/projects/${encodeURIComponent(projectSlug)}/debug`,
      { method: 'POST' }
    );
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to debug project: ${error.message}`);
    }
    throw new Error('Failed to debug project');
  }
}

export async function getProjectSecurity(projectSlug: string): Promise<SecurityReportResponse> {
  try {
    return await request<SecurityReportResponse>(`/projects/${encodeURIComponent(projectSlug)}/security`);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to audit project security: ${error.message}`);
    }
    throw new Error('Failed to audit project security');
  }
}

export async function getProjectDeployment(projectSlug: string): Promise<DeploymentReportResponse> {
  try {
    return await request<DeploymentReportResponse>(`/projects/${encodeURIComponent(projectSlug)}/deployment`);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch deployment configuration: ${error.message}`);
    }
    throw new Error('Failed to fetch deployment configuration');
  }
}

export interface GenerateImageResponse {
  prompt: string;
  width: number;
  height: number;
  seed: number;
  image_url: string;
}

export async function generateImage(prompt: string, width = 512, height = 512, seed?: number): Promise<GenerateImageResponse> {
  try {
    return await request<GenerateImageResponse>('/api/generate-image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt, width, height, seed }),
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to generate image: ${error.message}`);
    }

    throw new Error('Failed to generate image');
  }
}

export interface VideoScene {
  id: number;
  title: string;
  subtitle: string;
  type: string;
  duration: number;
  color: string;
  accent: string;
  voiceover: string;
}

export interface GenerateVideoResponse {
  prompt: string;
  width: number;
  height: number;
  theme?: string;
  seed: number;
  duration_seconds?: number;
  scenes?: VideoScene[];
  audio_script?: string;
  video_url: string;
}

export async function generateVideo(
  prompt: string,
  width = 1280,
  height = 720,
  theme = "cyberpunk",
  seed?: number,
): Promise<GenerateVideoResponse> {
  try {
    return await request<GenerateVideoResponse>('/api/generate-video', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt, width, height, theme, seed }),
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to generate video: ${error.message}`);
    }

    throw new Error('Failed to generate video');
  }
}

export interface ExplainProjectResponse {
  project_name: string;
  project_type: string;
  modules: string[];
  tech_stack: {
    frontend: string;
    backend: string;
    database: string;
  };
  narration_script: string;
  summary: string;
}

export async function explainProject(
  prompt: string,
  projectSlug?: string,
  language = "en",
): Promise<ExplainProjectResponse> {
  try {
    return await request<ExplainProjectResponse>('/api/explain-project', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt, project_slug: projectSlug, language }),
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to explain project: ${error.message}`);
    }

    throw new Error('Failed to explain project');
  }
}

export async function buildProject(
  projectSlug: string,
  onProgress?: (phase: string) => void,
): Promise<BuildProjectResponse> {
  try {
    const projectPath = `/projects/${encodeURIComponent(projectSlug)}/build`;
    let result = await request<BuildProjectResponse>(projectPath, {
      method: 'POST',
    });
    const startedAt = Date.now();
    while (result.status === 'queued' || result.status === 'installing' || result.status === 'building') {
      onProgress?.(result.phase);
      if (Date.now() - startedAt > 11 * 60 * 1000) {
        throw new Error('Frontend build status polling timed out. Check the backend build logs and try again.');
      }
      await new Promise((resolve) => window.setTimeout(resolve, 1500));
      result = await request<BuildProjectResponse>(projectPath);
    }
    onProgress?.(result.phase);
    return result;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to build project: ${error.message}`);
    }

    throw new Error('Failed to build project');
  }
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  created_at?: number;
}

export interface AuthResponse {
  status: string;
  message: string;
  user: AuthUser;
  token?: string;
}

export async function registerUser(
  username: string,
  email: string,
  password: string,
  fullName = ""
): Promise<AuthResponse> {
  return await request<AuthResponse>('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password, full_name: fullName }),
  });
}

export async function loginUser(
  login: string,
  password: string
): Promise<AuthResponse> {
  return await request<AuthResponse>('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login, password }),
  });
}

export async function getAuthMe(token: string): Promise<{ status: string; user: AuthUser }> {
  return await request<{ status: string; user: AuthUser }>('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function logoutUser(): Promise<{ status: string }> {
  try {
    return await request<{ status: string }>('/api/auth/logout', { method: 'POST' });
  } catch {
    return { status: 'success' };
  }
}
