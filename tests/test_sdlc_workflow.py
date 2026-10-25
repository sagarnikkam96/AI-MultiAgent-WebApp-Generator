"""Tests for the staged, approval-gated SDLC workflow."""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.orchestrator import MultiAgentOrchestrator
from app.agents.backend_schema import BackendBlueprint
from app.agents.database_schema import DatabaseBlueprint
from app.agents.planner_schema import ProjectPlan
from app.agents.schemas import RequirementSchema
from app.main import SDLCGenerationRequest, generate_approved_sdlc
from fastapi import HTTPException


class TestSDLCWorkflow(unittest.TestCase):
    def setUp(self):
        self.orchestrator = MultiAgentOrchestrator()
        self.prompt = "Build a task management system with projects, tasks, and comments"

    def test_plan_sdlc_returns_srs_and_complete_design(self):
        plan = self.orchestrator.plan_sdlc(self.prompt, language="en")

        self.assertEqual(plan["srs"]["project_name"], plan["requirements"]["project_name"])
        self.assertTrue(plan["srs"]["functional_requirements"])
        self.assertTrue(plan["srs"]["acceptance_criteria"])
        self.assertTrue(plan["project_plan"]["system_architecture"])
        self.assertTrue(plan["backend_blueprint"]["endpoints"])
        self.assertTrue(plan["database_blueprint"]["entities"])

    def test_run_uses_submitted_approved_design(self):
        plan = self.orchestrator.plan_sdlc(self.prompt)
        requirements = RequirementSchema.model_validate(plan["requirements"])
        project_plan = ProjectPlan.model_validate(plan["project_plan"])
        backend_blueprint = BackendBlueprint.model_validate(plan["backend_blueprint"])
        database_blueprint = DatabaseBlueprint.model_validate(plan["database_blueprint"])

        self.orchestrator.requirement_agent.analyze = Mock(side_effect=AssertionError("requirements were re-created"))
        self.orchestrator.planner_agent.plan = Mock(side_effect=AssertionError("design plan was re-created"))
        self.orchestrator.backend_agent.generate = Mock(side_effect=AssertionError("API design was re-created"))
        self.orchestrator.database_agent.generate = Mock(side_effect=AssertionError("database design was re-created"))
        self.orchestrator.code_agent.generate = Mock(return_value={
            "project_name": requirements.project_name,
            "project_slug": None,
            "project_path": None,
            "files_created": [],
            "files_count": 0,
        })
        self.orchestrator.ollama_client.generate = Mock(return_value="Architecture summary")
        self.orchestrator.hybrid_engine.generate_narration_script = Mock(return_value="Narration")

        result = self.orchestrator.run(
            self.prompt,
            requirements=requirements,
            project_plan=project_plan,
            backend_blueprint=backend_blueprint,
            database_blueprint=database_blueprint,
        )

        self.assertEqual(result["project_plan"]["project_name"], project_plan.project_name)
        design_context = self.orchestrator.code_agent.generate.call_args.kwargs["design_context"]
        self.assertEqual(design_context["project_plan"]["project_name"], project_plan.project_name)
        self.orchestrator.requirement_agent.analyze.assert_not_called()
        self.orchestrator.planner_agent.plan.assert_not_called()

    def test_generation_rejects_unapproved_design(self):
        plan = self.orchestrator.plan_sdlc(self.prompt)
        request = SDLCGenerationRequest(
            user_prompt=self.prompt,
            approved=False,
            requirements=plan["requirements"],
            project_plan=plan["project_plan"],
            backend_blueprint=plan["backend_blueprint"],
            database_blueprint=plan["database_blueprint"],
        )

        with self.assertRaises(HTTPException) as raised:
            generate_approved_sdlc(request)

        self.assertEqual(raised.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
