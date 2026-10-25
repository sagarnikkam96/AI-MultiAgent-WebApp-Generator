import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.code_agent import UserPromptProvider
from app.language_catalog import LANGUAGE_NAMES, output_language_instruction
from app.main import AnalyzeRequest


class TestLanguageSupport(unittest.TestCase):
    def test_catalog_contains_twenty_output_languages_including_existing_options(self):
        self.assertEqual(len(LANGUAGE_NAMES), 20)
        self.assertTrue({"en", "hi", "kn", "mr", "te"}.issubset(LANGUAGE_NAMES))
        self.assertTrue({"bn", "ta", "gu", "ml", "pa", "or", "as", "ur"}.issubset(LANGUAGE_NAMES))

    def test_generation_prompt_requires_selected_language_for_user_facing_copy(self):
        prompt = UserPromptProvider("Build a clinic app", language="ta").get_prompt()

        self.assertIn("Tamil (language code: ta)", prompt)
        self.assertIn("form labels, placeholders, validation messages", prompt)
        self.assertIn("Do not mix in English", prompt)

    def test_unsupported_output_language_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported output language"):
            output_language_instruction("xx")

    def test_api_request_accepts_new_language_and_rejects_unknown_codes(self):
        request = AnalyzeRequest(user_prompt="Clinic booking app", language="bn")
        self.assertEqual(request.language, "bn")

        with self.assertRaisesRegex(ValueError, "Unsupported output language"):
            AnalyzeRequest(user_prompt="Clinic booking app", language="xx")


if __name__ == "__main__":
    unittest.main()
