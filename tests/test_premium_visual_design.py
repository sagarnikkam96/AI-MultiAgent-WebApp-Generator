"""Tests for safe, staged premium visual upgrades."""

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import HTTPException

from app.agents.schemas import TestingReport
from app.main import (
    PremiumDesignRequest,
    accept_premium_design,
    create_premium_design_preview,
    premium_design_preview,
    reject_premium_design,
)
from app.visual_design.engine import PremiumDesignEngine
from app.code_generator.frontend_generator import FrontendGenerator


class TestPremiumDesignEngine(unittest.TestCase):
    def test_prompt_rules_select_contextual_style(self):
        engine = PremiumDesignEngine()
        direction = engine.create_art_direction("Create an organic sustainable farm marketplace", "auto")

        self.assertEqual(direction["personality"], "organic")
        self.assertEqual(direction["source"], "prompt_rules")
        self.assertIn("nature", direction["imagery_direction"])

    def test_railway_prompt_selects_a_distinct_rail_palette(self):
        direction = PremiumDesignEngine().create_art_direction(
            "Build a railway management system for trains, stations and schedules"
        )

        self.assertEqual(direction["personality"], "futuristic")
        self.assertEqual(direction["palette"]["accent"], "#e3a83b")
        self.assertIn("railway", direction["rationale"].casefold())

    def test_local_model_style_is_constrained_and_recorded(self):
        model = Mock()
        model.generate.return_value = (
            '{"personality":"editorial","rationale":"Readable product content.",'
            '"imagery":"Use existing project imagery."}'
        )
        direction = PremiumDesignEngine(model).create_art_direction("A library catalog")

        self.assertEqual(direction["personality"], "editorial")
        self.assertEqual(direction["source"], "local_model")

    def test_css_is_responsive_accessible_and_asset_free(self):
        engine = PremiumDesignEngine()
        direction = engine.create_art_direction("A minimalist finance workspace", "minimalist")
        css = engine.create_css(direction)

        self.assertEqual(engine.validate_css(css), [])
        self.assertIn(".topbar", css)
        self.assertIn("focus-visible", css)
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertNotIn("url(", css)

    def test_visual_personalities_select_distinct_layout_tokens(self):
        engine = PremiumDesignEngine()
        editorial = engine.create_css(engine.create_art_direction("Editorial journal", "editorial"))
        minimalist = engine.create_css(engine.create_art_direction("Simple workspace", "minimalist"))

        self.assertIn("--premium-sidebar-width: 238px", editorial)
        self.assertIn("--premium-layout-gap: 30px", editorial)
        self.assertIn("--premium-sidebar-width: 240px", minimalist)
        self.assertIn("--premium-layout-gap: 16px", minimalist)

    def test_css_replacement_preserves_custom_styles_around_owned_block(self):
        engine = PremiumDesignEngine()
        current = (
            ".existing { color: black; }\n"
            + engine.create_css(engine.create_art_direction("cinematic project", "cinematic"))
            + "\n.user-custom { letter-spacing: .02em; }\n"
        )
        replacement = engine.create_css(engine.create_art_direction("organic project", "organic"))
        updated = engine.replace_css(current, replacement)

        self.assertEqual(updated.count("PREMIUM_DESIGN_BEGIN"), 1)
        self.assertIn("Premium visual direction: organic", updated)
        self.assertNotIn("Premium visual direction: cinematic", updated)
        self.assertIn(".existing { color: black; }", updated)
        self.assertIn(".user-custom { letter-spacing: .02em; }", updated)

    def test_new_generated_projects_include_prompt_selected_visual_direction(self):
        generated_files = FrontendGenerator()._build_frontend_files(
            "Build a luxury real estate portfolio",
            "Property Portfolio",
        )
        stylesheet = next(file.content for file in generated_files if file.path.endswith("/src/styles.css"))

        self.assertIn("Premium visual direction: luxury", stylesheet)
        self.assertIn("prefers-reduced-motion: reduce", stylesheet)

    def test_generated_layout_matches_reference_hierarchy_responsively(self):
        generated_files = FrontendGenerator()._build_frontend_files(
            "Build a railway management system for trains, routes, stations, and schedules",
            "Railway Operations",
        )
        stylesheet = next(file.content for file in generated_files if file.path.endswith("/src/styles.css"))

        self.assertIn("grid-template-columns: minmax(0, 1.15fr) minmax(210px, .85fr) minmax(132px, .52fr)", stylesheet)
        self.assertIn(".domain-hero-stats", stylesheet)
        self.assertIn(".dashboard-card:nth-child(even)", stylesheet)
        self.assertIn("@media (max-width: 980px)", stylesheet)
        self.assertIn("@media (max-width: 640px)", stylesheet)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", stylesheet)


class TestPremiumDesignWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="premium-design-test-")
        self.root = Path(self.temp.name)
        self.slug = "visual_project"
        self.project = self.root / "projects" / self.slug
        self.frontend = self.project / "frontend"
        self.styles = self.frontend / "src" / "styles.css"
        self.app_source = self.frontend / "src" / "App.tsx"
        self.dist = self.frontend / "dist"
        self.styles.parent.mkdir(parents=True)
        self.dist.mkdir(parents=True)
        self.styles.write_text(":root { color: #fff; }\n", encoding="utf-8")
        self.app_source.write_text("export default function App() { return null; }\n", encoding="utf-8")
        (self.dist / "index.html").write_text("<html><head></head><body>built</body></html>", encoding="utf-8")
        (self.dist / "assets").mkdir()
        (self.dist / "assets" / "app.js").write_text("existing app bundle", encoding="utf-8")

        self.patchers = [
            patch("app.main.PROJECTS_ROOT", self.root / "projects"),
            patch("app.main.EXPORTS_ROOT", self.root / "exports"),
            patch("app.main.PREMIUM_DESIGN_ROOT", self.root / "exports" / ".premium-design-previews"),
            patch("app.main.premium_design_engine", PremiumDesignEngine()),
            patch("app.main.orchestrator.testing_agent.test_project", return_value=TestingReport(is_valid=True)),
            patch("app.main.orchestrator._serialize", side_effect=lambda report: report.model_dump()),
            patch("app.main.shutil.which", return_value="npm"),
        ]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.temp.cleanup()

    def test_preview_is_staged_without_changing_project_files_and_can_be_rejected(self):
        original_css = self.styles.read_text(encoding="utf-8")
        original_app = self.app_source.read_text(encoding="utf-8")
        preview = create_premium_design_preview(
            self.slug,
            PremiumDesignRequest(user_prompt="A refined editorial journal", style="editorial"),
        )
        staged_html = premium_design_preview(self.slug, preview["preview_id"])

        self.assertIn("Premium visual direction: editorial", staged_html.body.decode("utf-8"))
        self.assertEqual(self.styles.read_text(encoding="utf-8"), original_css)
        self.assertEqual(self.app_source.read_text(encoding="utf-8"), original_app)

        rejected = reject_premium_design(self.slug, preview["preview_id"])
        self.assertTrue(rejected["rejected"])
        self.assertEqual(self.styles.read_text(encoding="utf-8"), original_css)

    def test_accept_applies_only_styles_and_builds_with_validation(self):
        original_app = self.app_source.read_text(encoding="utf-8")
        preview = create_premium_design_preview(
            self.slug,
            PremiumDesignRequest(user_prompt="A creative journal", style="creative"),
        )

        with patch("app.main.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout="built", stderr="")):
            result = accept_premium_design(self.slug, preview["preview_id"])

        accepted_css = self.styles.read_text(encoding="utf-8")
        self.assertTrue(result["accepted"])
        self.assertIn("Premium visual direction: creative", accepted_css)
        self.assertEqual(self.app_source.read_text(encoding="utf-8"), original_app)
        self.assertTrue((self.dist / "assets" / "app.js").is_file())

    def test_build_failure_rolls_back_styles_and_built_files(self):
        original_css = self.styles.read_text(encoding="utf-8")
        original_bundle = (self.dist / "assets" / "app.js").read_text(encoding="utf-8")
        preview = create_premium_design_preview(
            self.slug,
            PremiumDesignRequest(user_prompt="A bold product", style="bold"),
        )

        with patch("app.main.subprocess.run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="build error")):
            with self.assertRaises(HTTPException) as raised:
                accept_premium_design(self.slug, preview["preview_id"])

        self.assertEqual(raised.exception.status_code, 422)
        self.assertEqual(self.styles.read_text(encoding="utf-8"), original_css)
        self.assertEqual((self.dist / "assets" / "app.js").read_text(encoding="utf-8"), original_bundle)

    def test_changed_base_stylesheet_requires_new_preview(self):
        preview = create_premium_design_preview(
            self.slug,
            PremiumDesignRequest(user_prompt="A minimalist catalog", style="minimalist"),
        )
        self.styles.write_text(self.styles.read_text(encoding="utf-8") + "/* user change */\n", encoding="utf-8")

        with self.assertRaises(HTTPException) as raised:
            accept_premium_design(self.slug, preview["preview_id"])

        self.assertEqual(raised.exception.status_code, 409)
        self.assertIn("user change", self.styles.read_text(encoding="utf-8"))

    def test_a_project_can_receive_a_later_visual_revision(self):
        with patch("app.main.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")):
            first = create_premium_design_preview(
                self.slug,
                PremiumDesignRequest(user_prompt="An editorial journal", style="editorial"),
            )
            accept_premium_design(self.slug, first["preview_id"])
            second = create_premium_design_preview(
                self.slug,
                PremiumDesignRequest(user_prompt="An organic marketplace", style="organic"),
            )
            result = accept_premium_design(self.slug, second["preview_id"])

        final_css = self.styles.read_text(encoding="utf-8")
        self.assertTrue(result["accepted"])
        self.assertEqual(final_css.count("PREMIUM_DESIGN_BEGIN"), 1)
        self.assertIn("Premium visual direction: organic", final_css)
        self.assertNotIn("Premium visual direction: editorial", final_css)


if __name__ == "__main__":
    unittest.main()
