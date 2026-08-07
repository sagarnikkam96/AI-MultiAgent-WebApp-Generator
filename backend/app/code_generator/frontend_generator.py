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
