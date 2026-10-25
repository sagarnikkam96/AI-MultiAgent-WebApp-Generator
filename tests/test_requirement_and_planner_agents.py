"""Unit tests for RequirementAgent and PlannerAgent."""

import unittest
from pathlib import Path
import sys

# Ensure backend app is importable
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.requirement_agent import RequirementAgent
from app.agents.planner_agent import PlannerAgent


class TestRequirementAgent(unittest.TestCase):
    """Test suite for RequirementAgent domain analysis and structured outputs."""

    def setUp(self):
        self.agent = RequirementAgent()

    def test_hospital_management_extraction(self):
        prompt = "Build a Hospital Management System with patient records and doctor appointments"
        req = self.agent.analyze(prompt)
        self.assertEqual(req.domain, "Healthcare")
        self.assertIn("React", req.frontend)
        self.assertIn("FastAPI", req.backend)
        self.assertTrue(len(req.user_roles) > 0)
        self.assertTrue(any("Patient" in r or "Doctor" in r for r in req.user_roles))
        self.assertTrue(len(req.features) > 0)
        self.assertTrue(len(req.data_requirements) > 0)

    def test_ecommerce_extraction(self):
        prompt = "Create an online e-commerce store with product catalog and shopping cart"
        req = self.agent.analyze(prompt)
        self.assertEqual(req.domain, "E-Commerce")
        self.assertTrue(any("Product" in m or "Orders" in m or "Cart" in m for m in req.modules))
        self.assertTrue(any("Customer" in r or "Admin" in r for r in req.user_roles))

    def test_food_delivery_extraction(self):
        prompt = "Develop a food delivery application for restaurant ordering and rider dispatch"
        req = self.agent.analyze(prompt)
        self.assertEqual(req.domain, "Food Delivery")
        self.assertTrue(len(req.pages) > 0)
        self.assertTrue(len(req.functional_requirements) > 0)

    def test_multilingual_detection(self):
        prompt_hi = "Create a college management system in hindi"
        req_hi = self.agent.analyze(prompt_hi)
        self.assertEqual(req_hi.language, "hi")

        prompt_kn = "Build a finance app in kannada"
        req_kn = self.agent.analyze(prompt_kn)
        self.assertEqual(req_kn.language, "kn")

        prompt_mr = "Create an inventory system in marathi"
        req_mr = self.agent.analyze(prompt_mr)
        self.assertEqual(req_mr.language, "mr")

        prompt_te = "Build real estate app in telugu"
        req_te = self.agent.analyze(prompt_te)
        self.assertEqual(req_te.language, "te")


class TestPlannerAgent(unittest.TestCase):
    """Test suite for PlannerAgent architecture and workflow planning."""

    def setUp(self):
        self.req_agent = RequirementAgent()
        self.planner = PlannerAgent()

    def test_planning_generation(self):
        req = self.req_agent.analyze("Build an inventory management system with stock tracking")
        plan = self.planner.plan(req)

        self.assertTrue(len(plan.frontend_tasks) > 0)
        self.assertTrue(len(plan.backend_tasks) > 0)
        self.assertTrue(len(plan.database_tasks) > 0)
        self.assertTrue(len(plan.deployment_tasks) > 0)
        self.assertTrue(len(plan.pages) > 0)
        self.assertTrue(len(plan.components) > 0)
        self.assertTrue(len(plan.apis) > 0)
        self.assertTrue(len(plan.user_workflow) > 0)
        self.assertIn("Three-tier", plan.system_architecture)


if __name__ == "__main__":
    unittest.main()
