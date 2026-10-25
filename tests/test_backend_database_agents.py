"""Unit tests for BackendGenerationAgent and DatabaseGenerationAgent."""

import unittest
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.requirement_agent import RequirementAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.backend_agent import BackendGenerationAgent
from app.agents.database_agent import DatabaseGenerationAgent


class TestBackendAndDatabaseAgents(unittest.TestCase):
    """Test suite for domain-driven backend and database blueprints."""

    def setUp(self):
        self.req_agent = RequirementAgent()
        self.planner_agent = PlannerAgent()
        self.backend_agent = BackendGenerationAgent()
        self.db_agent = DatabaseGenerationAgent()

    def test_domain_specific_backend_routes(self):
        req_food = self.req_agent.analyze("Build an online food delivery system")
        plan_food = self.planner_agent.plan(req_food)
        bp_food = self.backend_agent.generate(plan_food)

        self.assertEqual(bp_food.framework, "FastAPI")
        paths = [ep.path for ep in bp_food.endpoints]
        self.assertIn("/health", paths)
        self.assertTrue(any("restaurant" in p or "order" in p or "menu" in p for p in paths))

    def test_dynamic_database_models_not_hardcoded(self):
        # 1. Hospital requirements
        req_hospital = self.req_agent.analyze("Build a hospital management app")
        db_hospital = self.db_agent.generate(req_hospital)
        self.assertTrue(any("patient" in t.lower() or "doctor" in t.lower() for t in db_hospital.tables))

        # 2. E-Commerce requirements
        req_ecom = self.req_agent.analyze("Build an e-commerce shopping platform")
        db_ecom = self.db_agent.generate(req_ecom)
        self.assertTrue(any("product" in t.lower() or "order" in t.lower() or "category" in t.lower() for t in db_ecom.tables))
        self.assertFalse(any("doctor" in t.lower() for t in db_ecom.tables))

        # 3. Education / College requirements
        req_edu = self.req_agent.analyze("Build a college campus management system")
        db_edu = self.db_agent.generate(req_edu)
        self.assertTrue(any("student" in t.lower() or "course" in t.lower() for t in db_edu.tables))
        self.assertFalse(any("patient" in t.lower() for t in db_edu.tables))


if __name__ == "__main__":
    unittest.main()
