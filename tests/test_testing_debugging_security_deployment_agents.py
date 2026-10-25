"""Unit tests for TestingAgent, DebuggingAgent, SecurityAgent, and DeploymentAgent."""

import unittest
from pathlib import Path
import shutil
import tempfile
import sys

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.testing_agent import TestingAgent
from app.agents.debugging_agent import DebuggingAgent
from app.agents.security_agent import SecurityAgent
from app.agents.deployment_agent import DeploymentAgent
from app.agents.requirement_agent import RequirementAgent
from app.agents.code_agent import CodeGenerationAgent


class TestQualityAgents(unittest.TestCase):
    """Test suite for validation, self-healing, security, and deployment agents."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="agent_test_"))
        cls.code_agent = CodeGenerationAgent()
        cls.req_agent = RequirementAgent()

        req = cls.req_agent.analyze("Build a task management kanban board with users and projects")
        cls.gen_res = cls.code_agent.generate(
            user_prompt="Build a task management kanban board with users and projects",
            requirements=req,
            base_path=cls.temp_dir,
        )
        slug = cls.gen_res["project_slug"]
        cls.project_dir = cls.temp_dir / "generated_projects" / slug

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_testing_agent_validates_generated_code(self):
        agent = TestingAgent()
        report = agent.test_project(self.project_dir)
        self.assertTrue(report.is_valid)
        self.assertTrue(report.passed_count > 10)
        self.assertEqual(len(report.errors), 0)

    def test_debugging_agent_self_healing(self):
        # Introduce a test error (OAuth2PasswordBearer missing import in routes.py)
        routes_file = self.project_dir / "backend" / "routers" / "routes.py"
        original_content = routes_file.read_text(encoding="utf-8")
        corrupted_content = "oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/login')\n" + original_content.replace(
            "from fastapi.security import OAuth2PasswordBearer\n", ""
        )
        routes_file.write_text(corrupted_content, encoding="utf-8")

        testing_agent = TestingAgent()
        bad_report = testing_agent.test_project(self.project_dir)
        self.assertFalse(bad_report.is_valid)

        # Run debugging agent
        debug_agent = DebuggingAgent()
        final_report, debug_rep = debug_agent.debug_loop(self.project_dir, initial_report=bad_report)
        self.assertTrue(final_report.is_valid)
        self.assertTrue(debug_rep.succeeded)
        self.assertTrue(len(debug_rep.fixes) > 0)

    def test_security_agent_audit(self):
        agent = SecurityAgent()
        report = agent.audit_project(self.project_dir)
        self.assertTrue(report.is_secure)
        self.assertGreaterEqual(report.score, 90)
        self.assertTrue(len(report.passed_checks) > 0)

    def test_deployment_agent_preparation(self):
        agent = DeploymentAgent()
        report = agent.prepare_deployment(self.project_dir, project_name="Task Management System")
        self.assertTrue(report.ready)
        self.assertTrue((self.project_dir / "backend" / "Dockerfile").is_file())
        self.assertTrue((self.project_dir / "frontend" / "Dockerfile").is_file())
        self.assertTrue((self.project_dir / "docker-compose.yml").is_file())
        self.assertTrue((self.project_dir / ".env.example").is_file())
        self.assertTrue((self.project_dir / "DEPLOYMENT.md").is_file())


if __name__ == "__main__":
    unittest.main()
