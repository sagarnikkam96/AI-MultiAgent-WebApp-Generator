from __future__ import annotations

import json
import re
from pathlib import Path
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
        """Generate a valid package.json deterministically using Python."""
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "private": True,
            "version": "0.0.1",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc -b && vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
            },
            "devDependencies": {
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0",
                "@types/node": "^20.0.0",
                "@vitejs/plugin-react": "^4.0.0",
                "typescript": "^5.0.0",
                "vite": "^5.0.0",
                "tslib": "^2.0.0",
            },
        }
        return json.dumps(package_json, indent=2)

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
        return (
            "<!doctype html>\n"
            "<html lang=\"en\">\n"
            "  <head>\n"
            "    <meta charset=\"UTF-8\">\n"
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            f"    <title>{project_name}</title>\n"
            "  </head>\n"
            "  <body>\n"
            "    <div id=\"root\"></div>\n"
            "    <script type=\"module\" src=\"/src/main.tsx\"></script>\n"
            "  </body>\n"
            "</html>\n"
        )

    def generate_tsx(self, project_name: str, requirements: str, filename: str | None = None) -> str:
        """Generate a single TSX source file (e.g. App, Login, Dashboard)."""
        component_name = Path(filename).name if filename else None
        if component_name == "App.tsx":
            return self.generate_app_tsx(project_name, requirements)
        if component_name == "Login.tsx":
            return self.generate_login_tsx(project_name, requirements)
        if component_name == "Dashboard.tsx":
            return self.generate_dashboard_tsx(project_name, requirements)
        if component_name in {"SectionOne.tsx", "SectionTwo.tsx", "Products.tsx", "Orders.tsx", "Students.tsx", "Courses.tsx"}:
            return self.generate_resource_component(component_name, project_name, requirements)

        component_name = self._component_name_from_filename(filename)
        prompt = self._build_component_prompt(project_name, requirements, component_name)
        generated_text = self._generate_text(prompt)
        cleaned_text = self._clean_generated_tsx(generated_text)
        self._validate_react_tsx_output(cleaned_text)
        return cleaned_text

    def generate_app_tsx(self, project_name: str, requirements: str) -> str:
        """Return a deterministic App component for the React frontend."""
        context = self._infer_domain_context(project_name, requirements)
        return (
            "import React from 'react';\n"
            "import Login from './Login';\n"
            "import Dashboard from './Dashboard';\n"
            "import SectionOne from './SectionOne';\n"
            "import SectionTwo from './SectionTwo';\n"
            "\n"
            "const App: React.FC = () => {\n"
            "  return (\n"
            "    <div className=\"app-shell\">\n"
            "      <aside className=\"sidebar\">\n"
            f"        <div className=\"brand\">{context['app_label']}</div>\n"
            "        <nav className=\"nav-list\">\n"
            "          <a href=\"#dashboard\" className=\"active\">Dashboard</a>\n"
            f"          <a href=\"#section-1\">{context['section_one']}</a>\n"
            f"          <a href=\"#section-2\">{context['section_two']}</a>\n"
            "          <a href=\"#quick-access\">Quick Access</a>\n"
            "        </nav>\n"
            "      </aside>\n"
            "      <main className=\"page-content\">\n"
            "        <header className=\"topbar\">\n"
            f"          <h1>{context['app_label']}</h1>\n"
            "          <div className=\"top-actions\">\n"
            "            <button type=\"button\">Create New</button>\n"
            "            <button type=\"button\">Insights</button>\n"
            "          </div>\n"
            "        </header>\n"
            "\n"
            "        <section id=\"dashboard\" className=\"content-block\">\n"
            "          <Dashboard />\n"
            "        </section>\n"
            "\n"
            "        <section id=\"section-1\" className=\"content-block grid-block\">\n"
            "          <div>\n"
            "            <SectionOne />\n"
            "          </div>\n"
            "          <div>\n"
            "            <SectionTwo />\n"
            "          </div>\n"
            "        </section>\n"
            "\n"
            "        <section id=\"quick-access\" className=\"content-block\">\n"
            "          <div className=\"panel\">\n"
            "            <h2>Quick Access</h2>\n"
            "            <Login />\n"
            "          </div>\n"
            "        </section>\n"
            "      </main>\n"
            "    </div>\n"
            "  );\n"
            "};\n"
            "\n"
            "export default App;\n"
        )

    def generate_login_tsx(self, project_name: str, requirements: str) -> str:
        """Return a deterministic Login component with no required props."""
        context = self._infer_domain_context(project_name, requirements)
        return (
            "import React from 'react';\n"
            "\n"
            "const Login: React.FC = () => {\n"
            "  const [email, setEmail] = React.useState('');\n"
            "  const [password, setPassword] = React.useState('');\n"
            "\n"
            "  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {\n"
            "    e.preventDefault();\n"
            "    console.log('Login submitted', { email, password });\n"
            "  };\n"
            "\n"
            "  return (\n"
            "    <div className=\"login-card\">\n"
            f"      <h2>Welcome to {context['app_label']}</h2>\n"
            "      <p className=\"muted\">Securely sign in to continue managing your workspace.</p>\n"
            "      <form onSubmit={handleSubmit}>\n"
            "        <label>\n"
            "          Email\n"
            "          <input\n"
            "            type=\"email\"\n"
            "            value={email}\n"
            "            onChange={(e) => setEmail(e.target.value)}\n"
            "            required\n"
            "          />\n"
            "        </label>\n"
            "        <label>\n"
            "          Password\n"
            "          <input\n"
            "            type=\"password\"\n"
            "            value={password}\n"
            "            onChange={(e) => setPassword(e.target.value)}\n"
            "            required\n"
            "          />\n"
            "        </label>\n"
            "        <button type=\"submit\">Sign In</button>\n"
            "      </form>\n"
            "    </div>\n"
            "  );\n"
            "};\n"
            "\n"
            "export default Login;\n"
        )

    def generate_dashboard_tsx(self, project_name: str, requirements: str) -> str:
        """Return a deterministic Dashboard component for the React frontend."""
        context = self._infer_domain_context(project_name, requirements)
        return (
            "import React from 'react';\n"
            "\n"
            "const Dashboard: React.FC = () => {\n"
            "  const stats = [\n"
            f"    {{ label: '{context['metric_one_name']}', value: '{context['metric_one_value']}' }},\n"
            f"    {{ label: '{context['metric_two_name']}', value: '{context['metric_two_value']}' }},\n"
            f"    {{ label: '{context['metric_three_name']}', value: '{context['metric_three_value']}' }},\n"
            f"    {{ label: '{context['metric_four_name']}', value: '{context['metric_four_value']}' }},\n"
            "  ];\n"
            "\n"
            "  return (\n"
            "    <div className=\"dashboard-grid\">\n"
            "      {stats.map((stat, index) => (\n"
            "        <div key={index} className=\"dashboard-card\">\n"
            "          <span className=\"stat-label\">{stat.label}</span>\n"
            "          <strong>{stat.value}</strong>\n"
            "        </div>\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "};\n"
            "\n"
            "export default Dashboard;\n"
        )

    def generate_resource_component(self, filename: str, project_name: str, requirements: str) -> str:
        """Return a deterministic resource list component from a filename."""
        resource_name = Path(filename).stem
        context = self._infer_domain_context(project_name, requirements)
        if resource_name.lower() == 'patients':
            return (
                "import React from 'react';\n"
                "\n"
                "interface Patient {\n"
                "  id: number;\n"
                "  name: string;\n"
                "  age: number;\n"
                "  status: string;\n"
                "}\n"
                "\n"
                "const Patients: React.FC = () => {\n"
                "  const records: Patient[] = [\n"
                "    { id: 1, name: 'Ava Johnson', age: 29, status: 'Checked in' },\n"
                "    { id: 2, name: 'Noah Carter', age: 42, status: 'Under review' },\n"
                "    { id: 3, name: 'Mia Patel', age: 36, status: 'Discharged' },\n"
                "  ];\n"
                "\n"
                "  return (\n"
                "    <div className=\"resource-card\">\n"
                "      <h2>Patient Records</h2>\n"
                "      <table>\n"
                "        <thead>\n"
                "          <tr>\n"
                "            <th>ID</th>\n"
                "            <th>Name</th>\n"
                "            <th>Age</th>\n"
                "            <th>Status</th>\n"
                "          </tr>\n"
                "        </thead>\n"
                "        <tbody>\n"
                "          {records.map((record) => (\n"
                "            <tr key={record.id}>\n"
                "              <td>{record.id}</td>\n"
                "              <td>{record.name}</td>\n"
                "              <td>{record.age}</td>\n"
                "              <td>{record.status}</td>\n"
                "            </tr>\n"
                "          ))}\n"
                "        </tbody>\n"
                "      </table>\n"
                "    </div>\n"
                "  );\n"
                "};\n"
                "\n"
                "export default Patients;\n"
            )
        if resource_name.lower() == 'doctors':
            return (
                "import React from 'react';\n"
                "\n"
                "interface Doctor {\n"
                "  id: number;\n"
                "  name: string;\n"
                "  specialty: string;\n"
                "  availability: string;\n"
                "}\n"
                "\n"
                "const Doctors: React.FC = () => {\n"
                "  const records: Doctor[] = [\n"
                "    { id: 1, name: 'Leo Walker', specialty: 'Cardiology', availability: 'Online' },\n"
                "    { id: 2, name: 'Chloe Reed', specialty: 'Neurology', availability: 'Offline' },\n"
                "    { id: 3, name: 'Mason Reed', specialty: 'Pediatrics', availability: 'Available' },\n"
                "  ];\n"
                "\n"
                "  return (\n"
                "    <div className=\"resource-card\">\n"
                "      <h2>Doctor Directory</h2>\n"
                "      <ul className=\"resource-list\">\n"
                "        {records.map((record) => (\n"
                "          <li key={record.id}>\n"
                "            <strong>{record.name}</strong> — {record.specialty} · {record.availability}\n"
                "          </li>\n"
                "        ))}\n"
                "      </ul>\n"
                "    </div>\n"
                "  );\n"
                "};\n"
                "\n"
                "export default Doctors;\n"
            )
        return (
            "import React from 'react';\n"
            "\n"
            f"const {resource_name}: React.FC = () => {{\n"
            "  const items = [\n"
            "    { id: 1, label: 'Example Item', detail: 'Active' },\n"
            "    { id: 2, label: 'Second Item', detail: 'Pending' },\n"
            "    { id: 3, label: 'Third Item', detail: 'Ready' },\n"
            "  ];\n"
            "\n"
            "  return (\n"
            "    <div className=\"resource-card\">\n"
            f"      <h2>{resource_name}</h2>\n"
            "      <ul className=\"resource-list\">\n"
            "        {items.map((item) => (\n"
            "          <li key={item.id}>\n"
            "            <strong>{item.label}</strong> — {item.detail}\n"
            "          </li>\n"
            "        ))}\n"
            "      </ul>\n"
            "    </div>\n"
            "  );\n"
            "};\n"
            "\n"
            f"export default {resource_name};\n"
        )

    def generate_styles_css(self, project_name: str, requirements: str) -> str:
        """Generate application CSS for the React project."""
        return (
            ":root {\n"
            "  color-scheme: dark;\n"
            "  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\n"
            "  background: #070b16;\n"
            "  color: #e2e8f0;\n"
            "  line-height: 1.5;\n"
            "}\n"
            "* { box-sizing: border-box; }\n"
            "html, body, #root { min-height: 100%; margin: 0; padding: 0; }\n"
            "body { margin: 0; background: radial-gradient(circle at top, rgba(56,189,248,0.16), transparent 36%), linear-gradient(180deg, #0f172a 0%, #020617 100%); }\n"
            "button, input, select, textarea { font: inherit; }\n"
            ".app-shell { display: grid; grid-template-columns: 280px 1fr; gap: 24px; min-height: 100vh; padding: 24px; }\n"
            "@media (max-width: 980px) { .app-shell { grid-template-columns: 1fr; padding: 16px; } }\n"
            ".sidebar { background: rgba(15, 23, 42, 0.96); border: 1px solid rgba(148, 163, 184, 0.08); border-radius: 28px; padding: 28px; display: flex; flex-direction: column; gap: 24px; }\n"
            ".brand { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 16px; }\n"
            ".nav-list { display: flex; flex-direction: column; gap: 12px; }\n"
            ".nav-list a { color: #cbd5e1; text-decoration: none; padding: 12px 16px; border-radius: 16px; transition: background 0.2s ease, color 0.2s ease; }\n"
            ".nav-list a:hover, .nav-list a.active { background: rgba(59, 130, 246, 0.2); color: #ffffff; }\n"
            ".page-content { display: flex; flex-direction: column; gap: 24px; }\n"
            ".topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 24px 28px; border-radius: 28px; background: rgba(15, 23, 42, 0.76); border: 1px solid rgba(148, 163, 184, 0.08); }\n"
            ".topbar h1 { margin: 0; font-size: clamp(1.75rem, 2vw, 2.5rem); }\n"
            ".top-actions { display: flex; gap: 12px; }\n"
            ".top-actions button, button { border: none; cursor: pointer; background: linear-gradient(135deg, #38bdf8, #818cf8); color: white; padding: 12px 18px; border-radius: 14px; transition: transform 0.2s ease, filter 0.2s ease; }\n"
            "button:hover { transform: translateY(-1px); filter: brightness(1.05); }\n"
            ".content-block { background: rgba(15, 23, 42, 0.82); border: 1px solid rgba(148, 163, 184, 0.08); border-radius: 28px; padding: 24px; }\n"
            ".grid-block { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; }\n"
            "@media (max-width: 980px) { .grid-block { grid-template-columns: 1fr; } }\n"
            ".dashboard-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; }\n"
            "@media (max-width: 980px) { .dashboard-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }\n"
            "@media (max-width: 640px) { .dashboard-grid { grid-template-columns: 1fr; } }\n"
            ".dashboard-card, .resource-card, .panel { background: rgba(30, 41, 59, 0.9); border-radius: 24px; padding: 22px; border: 1px solid rgba(148, 163, 184, 0.08); }\n"
            ".stat-label { display: block; color: #94a3b8; margin-bottom: 10px; }\n"
            ".resource-card h2, .panel h2 { margin-top: 0; margin-bottom: 16px; font-size: 1.1rem; }\n"
            ".resource-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }\n"
            ".resource-list li { padding: 14px 16px; border-radius: 18px; background: rgba(15, 23, 42, 0.92); border: 1px solid rgba(148, 163, 184, 0.08); }\n"
            "table { width: 100%; border-collapse: collapse; margin: 0; }\n"
            "th, td { text-align: left; padding: 14px 16px; border-bottom: 1px solid rgba(148, 163, 184, 0.12); }\n"
            "th { color: #cbd5e1; font-weight: 600; }\n"
            "tr:hover { background: rgba(71, 85, 105, 0.16); }\n"
            "label { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; color: #cbd5e1; }\n"
            "input { width: 100%; padding: 14px 16px; border-radius: 16px; border: 1px solid rgba(148, 163, 184, 0.18); background: rgba(255, 255, 255, 0.06); color: #e2e8f0; }\n"
            "input:focus { outline: none; border-color: #38bdf8; box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.15); }\n"
            ".login-card { display: grid; gap: 18px; }\n"
            ".login-card p.muted { color: #94a3b8; margin: 0 0 12px; }\n"
        )

    def _infer_domain_context(self, project_name: str, requirements: str) -> dict[str, str]:
        normalized = f"{project_name} {requirements}".lower()
        fallback = {
            'app_label': project_name or 'Modern Dashboard',
            'section_one': 'Overview',
            'section_two': 'Reports',
            'metric_one_name': 'Active users',
            'metric_two_name': 'Task completion',
            'metric_three_name': 'Engagement',
            'metric_four_name': 'Growth',
            'metric_one_value': '1,240',
            'metric_two_value': '82%',
            'metric_three_value': '5,300',
            'metric_four_value': '14%',
        }
        domains = [
            (['hospital', 'medical', 'clinic', 'patient', 'doctor', 'healthcare', 'appointment'], {
                'app_label': project_name or 'Health Dashboard',
                'section_one': 'Patients',
                'section_two': 'Doctors',
                'metric_one_name': 'Total Patients',
                'metric_two_name': 'Active Doctors',
                'metric_three_name': 'Open Appointments',
                'metric_four_name': 'Available Beds',
                'metric_one_value': '1,280',
                'metric_two_value': '72',
                'metric_three_value': '34',
                'metric_four_value': '18',
            }),
            (['e-commerce', 'ecommerce', 'shop', 'store', 'product', 'cart', 'order', 'checkout'], {
                'app_label': project_name or 'Commerce Dashboard',
                'section_one': 'Products',
                'section_two': 'Orders',
                'metric_one_name': 'Revenue',
                'metric_two_name': 'Orders',
                'metric_three_name': 'Active Carts',
                'metric_four_name': 'Conversion',
                'metric_one_value': '$86.2K',
                'metric_two_value': '453',
                'metric_three_value': '127',
                'metric_four_value': '4.6%',
            }),
            (['student', 'students', 'course', 'courses', 'teacher', 'faculty', 'campus', 'education'], {
                'app_label': project_name or 'Campus Dashboard',
                'section_one': 'Students',
                'section_two': 'Courses',
                'metric_one_name': 'Enrolled Students',
                'metric_two_name': 'Active Courses',
                'metric_three_name': 'Faculty',
                'metric_four_name': 'Completion Rate',
                'metric_one_value': '3,420',
                'metric_two_value': '92',
                'metric_three_value': '48',
                'metric_four_value': '87%',
            }),
            (['restaurant', 'menu', 'reservation', 'reservation', 'dining', 'chef', 'order'], {
                'app_label': project_name or 'Restaurant Dashboard',
                'section_one': 'Menu',
                'section_two': 'Orders',
                'metric_one_name': 'Daily Orders',
                'metric_two_name': 'Reservations',
                'metric_three_name': 'Available Tables',
                'metric_four_name': 'Customer Rating',
                'metric_one_value': '128',
                'metric_two_value': '24',
                'metric_three_value': '12',
                'metric_four_value': '4.8★',
            }),
            (['inventory', 'stock', 'warehouse', 'supplier', 'shipment', 'sku'], {
                'app_label': project_name or 'Inventory Dashboard',
                'section_one': 'Stock',
                'section_two': 'Suppliers',
                'metric_one_name': 'In-stock Items',
                'metric_two_name': 'Low Stock',
                'metric_three_name': 'Shipments',
                'metric_four_name': 'Turnover',
                'metric_one_value': '4,100',
                'metric_two_value': '73',
                'metric_three_value': '18',
                'metric_four_value': '2.4x',
            }),
            (['bank', 'finance', 'account', 'transaction', 'loan', 'balance', 'customer'], {
                'app_label': project_name or 'Finance Dashboard',
                'section_one': 'Accounts',
                'section_two': 'Transactions',
                'metric_one_name': 'Total Balance',
                'metric_two_name': 'Transactions',
                'metric_three_name': 'New Customers',
                'metric_four_name': 'Approval Rate',
                'metric_one_value': '$1.8M',
                'metric_two_value': '2,140',
                'metric_three_value': '312',
                'metric_four_value': '91%',
            }),
        ]
        for keywords, domain in domains:
            if any(keyword in normalized for keyword in keywords):
                return domain
        return fallback

    def _build_component_prompt(self, project_name: str, requirements: str, component_name: str | None) -> str:
        component_instructions = []
        if component_name:
            component_instructions.append(f"Name the default exported component {component_name}.")
            component_instructions.append(
                "Export it using `export default`."
            )
        else:
            component_instructions.append("Export a default React component.")

        component_instructions.append(
            "Do not require component props unless the file explicitly needs them for the specified feature.")
        component_instructions.append(
            "Use local state for form or UI behavior, and keep the component self-contained for Vite + React compatibility."
        )

        return (
            f"Generate a single React + TypeScript component file for project '{project_name}'. "
            f"The component should satisfy: {requirements}. "
            "Use React only. Never use Vue, Angular, Svelte, Solid, or any other frontend framework. "
            "Never import from 'vue'. Never use defineComponent(). Never use createApp(). "
            "Do not import './App.css' unless App.css is also generated deliberately. "
            "Do not import files that the generator does not create. "
            + " ".join(component_instructions)
            + " Return only valid TSX source code for that component, with no markdown fences, no explanation, and no additional text."
        )

    def _component_name_from_filename(self, filename: str | None) -> str | None:
        if not filename:
            return None
        return Path(filename).stem

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
            "Use React only. Never use Vue, Angular, Svelte, Solid, or any other frontend framework. "
            "Never import from 'vue'. Never use defineComponent(). Never use createApp(). "
            "Provide only valid TSX source code, with no markdown fences, no explanation, and no additional text. "
            "Do not import files that the generator does not create. "
            "Focus on a clean, modern structure and use TypeScript syntax compatible with Vite + React. "
            "If multiple files are necessary, return only one combined source file for the main React entry point."
        )

    def _strip_markdown_fences(self, generated_text: str) -> str:
        """Extract the first valid TSX fenced code block or remove Markdown fences if present."""
        fenced_blocks = re.findall(r'```(?:tsx?|typescript)?\s*\n?(.*?)\n?```', generated_text, flags=re.IGNORECASE | re.DOTALL)
        if fenced_blocks:
            for block in fenced_blocks:
                if self._contains_tsx_code(block):
                    return block.strip()
            return fenced_blocks[0].strip()

        cleaned_text = re.sub(r'```(?:tsx?|typescript)?\s*', '', generated_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'```\s*$', '', cleaned_text, flags=re.MULTILINE)
        return cleaned_text.strip()

    def _clean_generated_tsx(self, generated_text: str) -> str:
        """Extract a clean TSX source block from generated text, removing surrounding prose."""
        cleaned_text = self._strip_markdown_fences(generated_text)
        lines = [line.rstrip() for line in cleaned_text.splitlines()]

        start = 0
        while start < len(lines) and not self._is_tsx_code_line(lines[start], allow_comments=True):
            start += 1

        end = len(lines)
        while end > start and not self._is_tsx_code_line(lines[end - 1], allow_comments=True):
            end -= 1

        stripped_lines = lines[start:end]

        while stripped_lines and not stripped_lines[0].strip():
            stripped_lines.pop(0)
        while stripped_lines and not stripped_lines[-1].strip():
            stripped_lines.pop()

        return '\n'.join(stripped_lines)

    def _contains_tsx_code(self, text: str) -> bool:
        """Detect whether a block contains likely TSX source code."""
        return bool(re.search(r'\bimport\s+React\b|\bexport\b|\bconst\b.*React\.FC|<\w+|\binterface\b|\btype\b', text))

    def _is_tsx_code_line(self, line: str, allow_comments: bool = False) -> bool:
        """Recognize a line that belongs to TSX/TypeScript source rather than prose."""
        stripped = line.strip()
        if not stripped:
            return False

        if allow_comments and stripped.startswith(('//', '/*', '*')):
            return True

        code_patterns = [
            r'^import\b',
            r'^export\b',
            r'^const\b',
            r'^let\b',
            r'^var\b',
            r'^function\b',
            r'^class\b',
            r'^interface\b',
            r'^type\b',
            r'^enum\b',
            r'^namespace\b',
            r'^abstract\b',
            r'^declare\b',
            r'^async\b',
            r'^(?:if|switch|try|for|while|do|return|throw)\b',
            r'^\[',
            r'^\(',
            r'^[<>/]',
            r'^[{}]$',
            r'^[{}].*',
            r'^[^\s].*\{$',
            r'=>',
            r'=\s*',
            r'\bextends\b',
            r'\bimplements\b',
            r'\bReact\.FC\b',
            r'\buseState\b',
            r'\bJSX\b',
            r'\bReactDOM\b',
        ]
        for pattern in code_patterns:
            if re.search(pattern, stripped):
                return True

        return False

    def _validate_react_tsx_output(self, source: str) -> None:
        """Reject generated TSX that contains non-React framework code or forbidden imports."""
        forbidden_patterns = [
            r"\bfrom\s+['\"]vue['\"]",
            r"\bdefineComponent\s*\(",
            r"\bcreateApp\s*\(",
            r"\bfrom\s+['\"]@angular['\"]",
            r"\bfrom\s+['\"]svelte['\"]",
            r"\bfrom\s+['\"]solid-js['\"]",
            r"\bfrom\s+['\"]lit['\"]",
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, source):
                raise ValueError(
                    "Generated TSX contains forbidden framework code. "
                    "Ensure the generator returns React-only TSX without Vue, Angular, or Svelte constructs."
                )

    def generate_main_tsx(self) -> str:
        """Return a deterministic Vite React 18 entry file."""
        return (
            "import React from 'react';\n"
            "import ReactDOM from 'react-dom/client';\n"
            "import App from './App';\n"
            "import './styles.css';\n"
            "\n"
            "ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(\n"
            "  <React.StrictMode>\n"
            "    <App />\n"
            "  </React.StrictMode>\n"
            ");\n"
        )

    def generate_tsconfig_json(self) -> str:
        """Return the root tsconfig.json for Vite + React + TypeScript."""
        return (
            '{\n'
            '  "compilerOptions": {\n'
            '    "target": "ES2020",\n'
            '    "useDefineForClassFields": true,\n'
            '    "lib": ["DOM", "DOM.Iterable", "ES2020"],\n'
            '    "allowJs": false,\n'
            '    "skipLibCheck": true,\n'
            '    "esModuleInterop": true,\n'
            '    "allowSyntheticDefaultImports": true,\n'
            '    "strict": true,\n'
            '    "forceConsistentCasingInFileNames": true,\n'
            '    "module": "ESNext",\n'
            '    "moduleResolution": "bundler",\n'
            '    "resolveJsonModule": true,\n'
            '    "isolatedModules": true,\n'
            '    "noEmit": true,\n'
            '    "jsx": "react-jsx",\n'
            '    "incremental": true,\n'
            '    "types": ["vite/client"]\n'
            '  },\n'
            '  "include": ["src"],\n'
            '  "references": [{ "path": "./tsconfig.node.json" }]\n'
            '}'
        )

    def generate_tsconfig_app_json(self) -> str:
        """Return a tsconfig.app.json for application-specific TypeScript settings."""
        return (
            '{\n'
            '  "extends": "./tsconfig.json",\n'
            '  "compilerOptions": {\n'
            '    "noEmit": false,\n'
            '    "outDir": "dist"\n'
            '  },\n'
            '  "include": ["src"]\n'
            '}'
        )

    def generate_tsconfig_node_json(self) -> str:
        """Return TypeScript configuration for Node/Vite config files."""
        return (
            '{\n'
            '  "compilerOptions": {\n'
            '    "module": "ESNext",\n'
            '    "moduleResolution": "bundler",\n'
            '    "target": "ES2020",\n'
            '    "lib": ["ES2020", "DOM"],\n'
            '    "types": ["node"],\n'
            '    "allowSyntheticDefaultImports": true,\n'
            '    "composite": true\n'
            '  },\n'
            '  "include": ["vite.config.ts"]\n'
            '}'
        )

    def generate_vite_config_ts(self) -> str:
        """Return a deterministic Vite config file using React plugin."""
        return (
            "import { defineConfig } from 'vite';\n"
            "import react from '@vitejs/plugin-react';\n"
            "\n"
            "export default defineConfig({\n"
            "  plugins: [react()],\n"
            "});\n"
        )

    def _build_frontend_files(self, prompt: str) -> list[GeneratedFile]:
        """Construct the initial frontend file list."""
        project_slug = self._project_slug(prompt)
        project_root = f"generated_projects/{project_slug}/frontend"
        return [
            GeneratedFile(
                path=f"{project_root}/src/App.tsx",
                content=self.generate_tsx(project_slug, prompt, filename='src/App.tsx'),
            ),
            GeneratedFile(
                path=f"{project_root}/src/Login.tsx",
                content=self.generate_tsx(project_slug, prompt, filename='src/Login.tsx'),
            ),
            GeneratedFile(
                path=f"{project_root}/src/Dashboard.tsx",
                content=self.generate_tsx(project_slug, prompt, filename='src/Dashboard.tsx'),
            ),
            GeneratedFile(
                path=f"{project_root}/src/SectionOne.tsx",
                content=self.generate_tsx(project_slug, prompt, filename='src/SectionOne.tsx'),
            ),
            GeneratedFile(
                path=f"{project_root}/src/SectionTwo.tsx",
                content=self.generate_tsx(project_slug, prompt, filename='src/SectionTwo.tsx'),
            ),
            GeneratedFile(
                path=f"{project_root}/src/main.tsx",
                content=self.generate_main_tsx(),
            ),
            GeneratedFile(
                path=f"{project_root}/src/styles.css",
                content=self.generate_styles_css(project_slug, prompt),
            ),
            GeneratedFile(
                path=f"{project_root}/tsconfig.json",
                content=self.generate_tsconfig_json(),
            ),
            GeneratedFile(
                path=f"{project_root}/tsconfig.app.json",
                content=self.generate_tsconfig_app_json(),
            ),
            GeneratedFile(
                path=f"{project_root}/tsconfig.node.json",
                content=self.generate_tsconfig_node_json(),
            ),
            GeneratedFile(
                path=f"{project_root}/vite.config.ts",
                content=self.generate_vite_config_ts(),
            ),
        ]

    def _project_slug(self, requirements: str) -> str:
        text = requirements.lower()
        text = re.sub(r"[^a-z0-9\s-]", " ", text)
        text = re.sub(
            r"\b(build|create|generate|develop|design|application|app|system|using|with|and|or|for|the|a|an|react|fastapi|postgres|postgresql|login|signup|register|authentication|auth|jwt|token|users|user|tasks|task|patients|doctors|billing|products|cart|orders)\b",
            " ",
            text,
        )
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return "generated_project"
        slug = "_".join(text.split()[:4])
        return slug[:50].strip("_") or "generated_project"

