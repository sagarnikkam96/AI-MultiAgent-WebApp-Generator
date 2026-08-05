const API_BASE_URL = 'http://127.0.0.1:8000';

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
    return await request<{ message: string; status: string; version: string }>('/');
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
