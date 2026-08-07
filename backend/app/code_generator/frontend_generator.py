from __future__ import annotations

import re
from typing import Protocol

from .code_generator import CodeGenerator, PromptProvider
from .code_schema import GeneratedFile


class FrontendGenerator(CodeGenerator):
    """Generates frontend code artifacts for Version 2."""

    def generate(self, project_name: str, requirements: str) -> str:
        """Generate React + TypeScript frontend source code using the Ollama client."""
        prompt = self._build_generation_prompt(project_name, requirements)
        generated_text = self._generate_text(prompt)
        return self._strip_markdown_fences(generated_text).strip()

    def generate_package_json(self, project_name: str, requirements: str) -> str:
        """Generate a package.json using a dedicated prompt. Returns raw LLM response.

        The response is intentionally returned un-parsed so the caller (FileWriter)
        can log and validate the raw LLM output before writing to disk.
        """
        prompt = self._build_package_json_prompt(project_name, requirements)
        return self._generate_text(prompt)

    def _build_package_json_prompt(self, project_name: str, requirements: str) -> str:
        """Build a strict prompt asking the LLM to return only a valid package.json object.

        The prompt emphasizes that only JSON must be returned, no markdown fences,
        and no additional explanation.
        """
        return (
            f"Generate a valid `package.json` file (JSON object) for a React + TypeScript project named '{project_name}'. "
            "Return ONLY the raw JSON object — nothing else: no markdown fences, no explanation, no extra text. "
            "Include typical Vite + React + TypeScript devDependencies and scripts for building and starting the app. "
            f"Project requirements: {requirements}."
        )

    def generate_index_html(self, project_name: str, requirements: str) -> str:
        """Generate an index.html for Vite that loads the React app."""
        prompt = (
            f"Generate a Vite-compatible index.html file for a React + TypeScript app named '{project_name}'. "
            "Return only the HTML file contents, without markdown fences or extra text."
        )
        generated_text = self._generate_text(prompt)
        return self._strip_markdown_fences(generated_text).strip()

    def generate_tsx(self, project_name: str, requirements: str) -> str:
        """Generate a single TSX source file (e.g. App, Login, Dashboard)."""
        prompt = (
            f"Generate a single React + TypeScript component file for project '{project_name}'. "
            f"The component should satisfy: {requirements}. "
            "Return only the TypeScript source code for that component, without markdown fences or extra explanation."
        )
        generated_text = self._generate_text(prompt)
        return self._strip_markdown_fences(generated_text).strip()

    def generate_files(self, prompt_provider: PromptProvider) -> list[GeneratedFile]:
        """Create frontend files from the given prompt provider."""
        prompt = prompt_provider.get_prompt()
        return self._build_frontend_files(prompt)

    def _build_generation_prompt(self, project_name: str, requirements: str) -> str:
        """Build the prompt sent to Ollama for frontend generation."""
        return (
            f"Generate React + TypeScript source code for a frontend application named '{project_name}'. "
            "The frontend should satisfy these requirements: "
            f"{requirements}. "
            "Provide only the source code for the React component(s), without any markdown fences, explanation, or additional text. "
            "Focus on a clean, modern structure and use TypeScript syntax compatible with Vite + React. "
            "If multiple files are necessary, return only one combined source file for the main React entry point."
        )

    def _strip_markdown_fences(self, generated_text: str) -> str:
        """Remove Markdown code fences from the generated output."""
        cleaned_text = re.sub(r'```(?:tsx?|typescript)?\n', '', generated_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'```\s*$', '', cleaned_text, flags=re.MULTILINE)
        return cleaned_text

    def _build_frontend_files(self, prompt: str) -> list[GeneratedFile]:
        """Construct the initial frontend file list."""
        # TODO: implement frontend generation using Ollama and structured prompts
        return [
            GeneratedFile(
                path="frontend/src/App.tsx",
                content=self._frontend_app_placeholder(prompt),
            ),
            GeneratedFile(
                path="frontend/src/main.tsx",
                content=self._frontend_main_placeholder(),
            ),
        ]

    def _frontend_app_placeholder(self, prompt: str) -> str:
        """Return a simple placeholder App component."""
        return (
            "import React from 'react';\n"
            "\n"
            "const App: React.FC = () => {\n"
            "  return (\n"
            "    <div>\n"
            "      <h1>Generated Frontend</h1>\n"
            "      <p>{prompt}</p>\n"
            "    </div>\n"
            "  );\n"
            "};\n"
            "\n"
            "export default App;\n"
        ).replace("{prompt}", prompt)

    def _frontend_main_placeholder(self) -> str:
        """Return a placeholder Vite React entry file."""
        return (
            "import React from 'react';\n"
            "import ReactDOM from 'react-dom/client';\n"
            "import App from './App';\n"
            "\n"
            "ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(\n"
            "  <React.StrictMode>\n"
            "    <App />\n"
            "  </React.StrictMode>\n"
            ");\n"
        )
