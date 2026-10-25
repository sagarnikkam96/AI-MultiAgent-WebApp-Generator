"""End-to-end integration tests for the full 9-agent autonomous pipeline."""

import unittest
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.orchestrator import MultiAgentOrchestrator


class TestE2EPipeline(unittest.TestCase):
    """End-to-end multi-agent execution pipeline verification."""

    def setUp(self):
        self.orchestrator = MultiAgentOrchestrator()

    def test_full_pipeline_healthcare(self):
        result = self.orchestrator.run("Build a hospital clinic appointment system with patient registration")
        self.assertIsNotNone(result.get("requirements"))
        self.assertIsNotNone(result.get("project_plan"))
        self.assertIsNotNone(result.get("backend_blueprint"))
        self.assertIsNotNone(result.get("database_blueprint"))
        self.assertIsNotNone(result.get("generated_project"))

        gen = result["generated_project"]
        self.assertTrue(gen["files_count"] > 10)
        self.assertIsNotNone(gen["project_slug"])

        test_rep = result.get("testing_report")
        self.assertIsNotNone(test_rep)
        self.assertTrue(test_rep["is_valid"])

        sec_rep = result.get("security_report")
        self.assertIsNotNone(sec_rep)
        self.assertTrue(sec_rep["is_secure"])

        dep_rep = result.get("deployment_report")
        self.assertIsNotNone(dep_rep)
        self.assertTrue(dep_rep["ready"])

    def test_full_pipeline_ecommerce(self):
        result = self.orchestrator.run("Create an e-commerce shopping web application with cart and products")
        self.assertEqual(result["requirements"]["domain"], "E-Commerce")
        self.assertTrue(result["generated_project"]["files_count"] > 10)
        self.assertTrue(result["testing_report"]["is_valid"])


if __name__ == "__main__":
    unittest.main()
