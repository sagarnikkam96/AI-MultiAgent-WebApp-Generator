import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app import main as main_module
from app.main import app
from app.api.auth import LoginRequest, RegisterRequest, login, register
from app.database import auth_db


class TestAuthEndpoints(unittest.TestCase):
    def test_project_history_endpoint_returns_only_the_signed_in_users_projects(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            database = root / "auth.db"
            projects_root = root / "generated_projects"
            with patch.object(auth_db, "DB_FILE", database), patch.object(main_module, "PROJECTS_ROOT", projects_root):
                owner = auth_db.register_user(
                    username="siteowner",
                    email="owner@example.test",
                    password="test-password",
                )
                other = auth_db.register_user(
                    username="siteviewer",
                    email="viewer@example.test",
                    password="test-password",
                )
                project = projects_root / "college_portal" / "frontend" / "dist"
                project.mkdir(parents=True)
                (project / "index.html").write_text("<html></html>", encoding="utf-8")

                main_module._record_user_project(
                    {
                        "generated_project": {
                            "project_slug": "college_portal",
                            "project_name": "College Portal",
                        }
                    },
                    {"id": owner["id"]},
                )
                owner_history = main_module.get_project_history({"id": owner["id"]})
                other_history = main_module.get_project_history({"id": other["id"]})

        self.assertEqual(owner_history["count"], 1)
        self.assertEqual(owner_history["projects"][0]["project_name"], "College Portal")
        self.assertTrue(owner_history["projects"][0]["built"])
        self.assertEqual(other_history["projects"], [])

    def test_generated_website_history_is_scoped_to_each_user(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "auth.db"
            with patch.object(auth_db, "DB_FILE", database):
                first_user = auth_db.register_user(
                    username="sagar",
                    email="sagar@example.test",
                    password="test-password",
                )
                second_user = auth_db.register_user(
                    username="another",
                    email="another@example.test",
                    password="test-password",
                )
                auth_db.record_generated_project(first_user["id"], "college_portal", "College Portal")

                first_history = auth_db.get_generated_projects(first_user["id"])
                second_history = auth_db.get_generated_projects(second_user["id"])

        self.assertEqual(len(first_history), 1)
        self.assertEqual(first_history[0]["project_slug"], "college_portal")
        self.assertEqual(first_history[0]["project_name"], "College Portal")
        self.assertEqual(second_history, [])

    def test_registration_and_login_succeed_with_sqlite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "auth.db"
            with patch.object(auth_db, "DB_FILE", database):
                registered = register(RegisterRequest(
                    username="testuser",
                    email="testuser@example.test",
                    password="test-password",
                    full_name="Test User",
                ))
                authenticated = login(LoginRequest(
                    login="testuser@example.test",
                    password="test-password",
                ))

        self.assertEqual(registered["status"], "success")
        self.assertEqual(authenticated["status"], "success")
        self.assertEqual(registered["user"]["id"], authenticated["user"]["id"])
        self.assertTrue(registered["token"])
        self.assertTrue(authenticated["token"])
        self.assertIsNotNone(app)

    def test_main_auth_routes_match_frontend_requests(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "auth.db"
            client = TestClient(app)
            with patch.object(auth_db, "DB_FILE", database):
                registered = client.post(
                    "/api/auth/register",
                    json={
                        "username": "routeuser",
                        "email": "routeuser@example.test",
                        "password": "test-password",
                        "full_name": "Route User",
                    },
                )
                logged_in = client.post(
                    "/api/auth/login",
                    json={"login": "routeuser@example.test", "password": "test-password"},
                )

        self.assertEqual(registered.status_code, 200)
        self.assertTrue(registered.json()["token"])
        self.assertEqual(logged_in.status_code, 200)
        self.assertEqual(logged_in.json()["user"]["email"], "routeuser@example.test")
        self.assertTrue(logged_in.json()["token"])


if __name__ == "__main__":
    unittest.main()
