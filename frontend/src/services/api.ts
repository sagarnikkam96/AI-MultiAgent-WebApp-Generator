// Requests are same-origin and proxied to the FastAPI backend by Vite (see
// vite.config.ts). Override with VITE_API_BASE_URL if needed, e.g.
//   VITE_API_BASE_URL=http://127.0.0.1:8000
const API_BASE_URL: string = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

interface RequirementAnalysisResponse {
  project_name: string;
  project_type: string;
  frontend: string;
  backend: string;
  database: string;
  authentication: boolean;
  modules: string[];
  validation_errors: string[];
}

interface AnalyzeProjectResponse {
  requirements: RequirementAnalysisResponse;
  project_plan: Record<string, unknown>;
  backend_blueprint: Record<string, unknown>;
  database_blueprint: Record<string, unknown>;
  ollama_response?: string | null;
  generated_project?: GeneratedProjectResponse;
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

export interface BuildProjectResponse {
  slug: string;
  install_success: boolean;
  build_success: boolean;
  built: boolean;
  install_log: string;
  build_log: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
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

export async function analyzeProject(userPrompt: string): Promise<AnalyzeProjectResponse> {
  try {
    return await request<AnalyzeProjectResponse>('/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_prompt: userPrompt }),
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to analyze project: ${error.message}`);
    }

    throw new Error('Failed to analyze project');
  }
}

export function downloadProjectZipUrl(projectSlug: string): string {
  return `${API_BASE_URL}/projects/${encodeURIComponent(projectSlug)}/download`;
}

export function projectPreviewUrl(projectSlug: string): string {
  return `${API_BASE_URL}/projects/${encodeURIComponent(projectSlug)}/preview`;
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

export async function buildProject(projectSlug: string): Promise<BuildProjectResponse> {
  try {
    return await request<BuildProjectResponse>(`/projects/${encodeURIComponent(projectSlug)}/build`, {
      method: 'POST',
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to build project: ${error.message}`);
    }

    throw new Error('Failed to build project');
  }
}
