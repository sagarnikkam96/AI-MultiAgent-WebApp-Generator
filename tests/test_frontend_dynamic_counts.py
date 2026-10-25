import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.code_generator.frontend_generator import FrontendGenerator
from app.code_generator.website_spec import derive_website_spec
from app.agents.database_agent import DatabaseGenerationAgent
from app.agents.requirement_agent import RequirementAgent
from app.code_generator.backend_generator import BackendGenerator


class TestFrontendDynamicCounts(unittest.TestCase):
    def setUp(self):
        self.generator = FrontendGenerator()

    def test_domain_modules_start_empty_and_report_live_counts(self):
        files = self.generator._build_frontend_files(
            "Build a hospital management system",
            "Hospital Management",
        )
        contents = {Path(file.path).name: file.content for file in files}

        self.assertIn("useState<PatientsRecord[]>([])", contents["Patients.tsx"])
        self.assertIn("res_data_hospital_management_patients", contents["Patients.tsx"])
        self.assertIn("onCountChange?.(next.length)", contents["Patients.tsx"])
        self.assertIn("onCountChange?.(restored.length)", contents["Patients.tsx"])
        self.assertIn("onCountChange={(count) => setEntityCounts", contents["App.tsx"])
        self.assertIn("entityCounts?.[stat.key] ??", contents["Dashboard.tsx"])
        self.assertNotIn("entityCounts?.[stat.key] ?? 0", contents["Dashboard.tsx"])
        self.assertNotIn("1,280", contents["Dashboard.tsx"])
        self.assertNotIn("1,280", contents["App.tsx"])
        self.assertTrue(all("value" not in metric for metric in derive_website_spec("hospital")["metrics"]))

    def test_dashboard_counts_are_dynamic_for_multiple_domains(self):
        for prompt, project_name, module in (
            ("college student teacher attendance system", "College Management", "Students"),
            ("hotel rooms bookings guests staff system", "Hotel Management", "Staff"),
        ):
            with self.subTest(project_name=project_name):
                files = self.generator._build_frontend_files(prompt, project_name)
                contents = {Path(file.path).name: file.content for file in files}

                self.assertIn("entityCounts?.[stat.key] ??", contents["Dashboard.tsx"])
                self.assertNotIn("entityCounts?.[stat.key] ?? 0", contents["Dashboard.tsx"])
                self.assertNotIn("3,420", contents["Dashboard.tsx"])
                self.assertIn(f"useState<{module}Record[]>([])", contents[f"{module}.tsx"])
                count_key = "staffs" if module == "Staff" else module.lower()
                self.assertIn(f"{count_key!r}: count", contents["App.tsx"])

    def test_generated_sites_include_domain_matched_branding_and_hero_photos(self):
        cases = (
            ("hospital patient doctor system", "My Campus Portal", "Doctors caring", "ambulance", 'd="M29 15h6', "cyan"),
            ("collage student course management", "My Learning Portal", "Students celebrating", "Bookshelves", 'd="M14 20c7', "indigo"),
            ("hotel management food service", "My Guest Portal", "Contemporary hotel exterior", "hotel guest room", 'd="M18 39h28', "rose"),
            ("reilve schedule management", "My Transit Portal", "Passenger train", "Green forest", 'd="M22 15h20', "cyan"),
        )

        for prompt, project_name, image_description, secondary_image_description, logo_shape, accent in cases:
            with self.subTest(project_name=project_name):
                files = self.generator._build_frontend_files(prompt, project_name)
                contents = {Path(file.path).name: file.content for file in files}

                self.assertIn("import brandMark from './assets/brand-mark.svg';", contents["App.tsx"])
                self.assertIn("domain-hero-image", contents["App.tsx"])
                self.assertIn("images.unsplash.com", contents["App.tsx"])
                self.assertEqual(contents["App.tsx"].count('className="domain-hero-image"'), 2)
                self.assertIn(f'<rect width="64" height="64" rx="20"', contents["brand-mark.svg"])
                self.assertIn(image_description, contents["App.tsx"])
                self.assertIn(secondary_image_description, contents["App.tsx"])
                self.assertIn(logo_shape, contents["brand-mark.svg"])
                accent_hex = {
                    "cyan": "#38bdf8",
                    "indigo": "#7868e8",
                    "rose": "#d47b83",
                }[accent]
                self.assertIn(f"const [accentColor, setAccentColor] = useState('{accent_hex}')", contents["App.tsx"])
                self.assertIn('aria-pressed={accentColor === palette.value}', contents["App.tsx"])
                self.assertIn("setAccentColor(palette.value)", contents["App.tsx"])

        rail_files = self.generator._build_frontend_files(
            "reilve schedule management",
            "Railway",
        )
        self.assertIn("Trains.tsx", {Path(file.path).name for file in rail_files})

    def test_railway_generation_stays_domain_consistent_and_uses_database_counts(self):
        prompt = "Build a Railway Management System for trains, routes, stations, schedules and passenger bookings"
        frontend_files = self.generator._build_frontend_files(prompt, "Railway Management")
        contents = {Path(file.path).name: file.content for file in frontend_files}

        self.assertIn("Schedules.tsx", contents)
        self.assertIn("'trains': 'Trains'", contents["languages.ts"])
        self.assertIn("'routes': 'Routes'", contents["languages.ts"])
        self.assertIn("Passenger train traveling along a railway", contents["App.tsx"])
        self.assertIn("Train Fleet", contents["Trains.tsx"])
        self.assertIn("Train Schedules", contents["Schedules.tsx"])
        self.assertNotIn("Patient", "\n".join(contents.values()))
        self.assertNotIn("Doctor", "\n".join(contents.values()))
        self.assertIn("http://127.0.0.1:8001", contents["App.tsx"])
        self.assertIn("fetch(`${API_BASE_URL}/counts`)", contents["App.tsx"])
        self.assertIn("Records saved in this browser", contents["App.tsx"])
        self.assertIn("?? '—'", contents["Dashboard.tsx"])
        self.assertIn("No trains have been added yet.", contents["Dashboard.tsx"])
        self.assertNotIn("2,450", "\n".join(contents.values()))
        self.assertNotIn("stat_1_val", self.generator._resolve_domain_palette(prompt))

        requirements = RequirementAgent().analyze(prompt)
        database_blueprint = DatabaseGenerationAgent().generate(requirements)
        self.assertIn("Train", database_blueprint.entities)
        self.assertIn("Route", database_blueprint.entities)
        self.assertIn("Station", database_blueprint.entities)
        self.assertIn("Schedule", database_blueprint.entities)
        self.assertIn("Booking", database_blueprint.entities)

        backend = BackendGenerator()._build_backend_files(prompt)
        routes = next(file.content for file in backend if file.path.endswith("/routers/routes.py"))
        services = next(file.content for file in backend if file.path.endswith("/services/services.py"))
        self.assertIn("@router.get('/counts')", routes)
        self.assertIn("'trains': db.query(Train).count()", routes)
        self.assertIn("'schedules': db.query(Schedule).count()", routes)
        self.assertNotIn("OAuth2PasswordBearer", routes)
        self.assertIn("Train(name=name, description=description)", services)
        self.assertNotIn("created_by_id=created_by_id)", services)

        auth_routes = next(
            file.content
            for file in BackendGenerator()._build_backend_files(
                f"{prompt} with login and JWT authentication"
            )
            if file.path.endswith("/routers/routes.py")
        )
        self.assertIn("current_user: User = Depends(get_current_user)", auth_routes)
        self.assertIn("db.query(Train).filter(Train.created_by_id == current_user.id).count()", auth_routes)

    def test_specific_project_title_prevents_competing_prompt_domain_from_taking_over(self):
        prompt = (
            "Build a railway management system for trains and routes. "
            "The user also mentioned patients, doctors, appointments, billing, and pharmacy."
        )
        files = self.generator._build_frontend_files(prompt, "railway_management_system")
        contents = {Path(file.path).name: file.content for file in files}

        self.assertIn("Passenger train traveling along a railway", contents["App.tsx"])
        self.assertIn("Railway & Transit Operations", contents["App.tsx"])
        self.assertIn("Coordinate trains, routes, stations, and schedules", contents["App.tsx"])
        self.assertIn("Trains.tsx", contents)
        self.assertNotIn("Healthcare & Clinical Management", contents["App.tsx"])
        self.assertNotIn("Coordinated Patient Care", contents["App.tsx"])
        self.assertNotIn("Patients.tsx", contents)

    def test_reference_quick_actions_keep_existing_site_features_reachable(self):
        files = self.generator._build_frontend_files(
            "Build a railway management system for trains, routes, and stations",
            "Railway Management System",
        )
        app = next(file.content for file in files if file.path.endswith("App.tsx"))
        stylesheet = next(file.content for file in files if file.path.endswith("styles.css"))

        for label in (
            "Add New Feature",
            "Create New",
            "Customize Site",
            "Add Media",
            "Reports &amp; Insights",
            "Sign in / Register",
        ):
            self.assertIn(label, app)
        self.assertIn("document.getElementById('media-upload')?.click()", app)
        self.assertIn('href="#reports"', app)
        self.assertIn(".top-actions", stylesheet)
        self.assertIn("@media (max-width: 980px)", stylesheet)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", stylesheet)

    def test_count_keys_match_generated_backend_pluralization(self):
        for component, expected in (
            ("Faculty", "faculties"),
            ("Category", "categories"),
            ("Attendance", "attendances"),
            ("Staff", "staffs"),
            ("Trains", "trains"),
        ):
            with self.subTest(component=component):
                self.assertEqual(self.generator._count_key(component), expected)

    def test_generated_frontend_documents_backend_api_configuration(self):
        prompt = "Build a railway management system"
        frontend = self.generator._build_frontend_files(prompt, "Railway")
        backend = BackendGenerator()._build_backend_files(prompt)
        frontend_files = {Path(file.path).name: file.content for file in frontend}
        backend_files = {Path(file.path).name: file.content for file in backend}

        self.assertEqual(frontend_files[".env.example"], "VITE_API_BASE_URL=http://127.0.0.1:8001\n")
        self.assertIn("VITE_API_BASE_URL", frontend_files["App.tsx"])
        self.assertIn("--port 8001", backend_files["README.md"])
        self.assertIn("http://127.0.0.1:8001", backend_files["README.md"])

    def test_explicit_modules_for_known_domain_are_added_to_navigation_and_generation(self):
        prompt = (
            "Build a railway operations app with modules: trains, routes, stations, "
            "schedules, staff, reports, and maintenance"
        )
        spec = derive_website_spec(prompt, "Rail Operations")
        files = self.generator._build_frontend_files(prompt, "Rail Operations")
        contents = {Path(file.path).name: file.content for file in files}

        self.assertIn("Staff", spec["components"])
        self.assertIn("Reports", spec["components"])
        self.assertIn("Maintenance", spec["components"])
        self.assertIn("Reports.tsx", contents)
        self.assertIn("Maintenance.tsx", contents)
        self.assertIn('"Reports"', contents["App.tsx"])
        self.assertIn('"Maintenance"', contents["App.tsx"])
        self.assertIn("'reports': count", contents["App.tsx"])

    def test_domain_matcher_handles_concept_overlap_without_hospital_leakage(self):
        files = self.generator._build_frontend_files(
            "Build a railway operations app for train schedules; this is not a hospital system",
            "Railway Operations",
        )
        contents = {Path(file.path).name: file.content for file in files}
        self.assertIn("Railway & Transit Operations", contents["App.tsx"])
        self.assertNotIn("Healthcare & Clinical Management", contents["App.tsx"])
        self.assertNotIn("Patient Directory", "\n".join(contents.values()))

    def test_generated_sites_restore_customizer_features_reports_and_media(self):
        prompt = "Build a restaurant management app for menus, orders, reservations, and staff"
        spec = derive_website_spec(prompt, "Restaurant Operations")
        files = self.generator._build_frontend_files(prompt, "Restaurant Operations")
        contents = {Path(file.path).name: file.content for file in files}
        app = contents["App.tsx"]
        styles = contents["styles.css"]

        for expected in (
            "Website &amp; Theme Customizer",
            "Reset defaults",
            "Save &amp; apply",
            "Reports &amp; Insights",
            "Media gallery",
            "Add a feature module",
            "floating-feature",
            "localStorage.setItem(STORAGE_KEY",
            "customFeatures.map((feature)",
            "setCustomFeatures((current)",
            "reportSearch",
            "URL.createObjectURL(file)",
            "Database records",
            "theme === 'light' ? 'light-mode' : 'dark-mode'",
            "'--bg-page': pageColor",
            "'--bg-card': cardColor",
            "'--bg-inner': innerColor",
            "document.documentElement, document.body, document.querySelector<HTMLElement>('.app-shell')",
            "const selectedPalette = palettes.find((palette) => palette.value === accentColor)",
            "light: ['#d7ebff', '#c3e0ff', '#a7cefa']",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, app)

        for component in spec["components"]:
            self.assertIn(f"{component}.tsx", contents)
            self.assertIn(f"import {component} from './{component}';", app)
        self.assertNotIn("Patient", "\n".join(contents.values()))
        self.assertNotIn("Doctor", "\n".join(contents.values()))
        self.assertIn(".app-shell.light-mode", styles)

    def test_custom_domain_modules_drive_the_generated_experience(self):
        prompt = (
            "Create a pet adoption app for users to manage pets, shelters, "
            "adoption applications, and foster homes."
        )
        spec = derive_website_spec(prompt, "PawPath")
        files = self.generator._build_frontend_files(prompt, "PawPath")
        contents = {Path(file.path).name: file.content for file in files}

        self.assertEqual(spec["key"], "generic")
        self.assertEqual(
            list(spec["module_labels"].values()),
            ["Pets", "Shelters", "Adoption Applications", "Foster Homes"],
        )
        for component in spec["components"]:
            self.assertRegex(component, r"^[A-Za-z][A-Za-z0-9]*$")
            self.assertIn(f"{component}.tsx", contents)
            self.assertIn(f"import {component} from './{component}';", contents["App.tsx"])
        self.assertIn("Manage Pets, Shelters, Adoption Applications, Foster Homes", contents["App.tsx"])
        self.assertIn('"Manage Pets, Shelters, Adoption Applications, Foster Homes"', contents["App.tsx"])
        self.assertIn("No pets have been added yet.", contents["Dashboard.tsx"])
        self.assertIn("{ label: 'Database Records', key: 'total' }", contents["Dashboard.tsx"])
        self.assertIn("domain-hero-art-card", contents["App.tsx"])
        self.assertNotIn("images.unsplash.com", contents["App.tsx"])
        self.assertIn("Adoption Applications", contents["AdoptionApplications.tsx"])
        self.assertIn("Adoption Application Name", contents["AdoptionApplications.tsx"])
        self.assertNotIn("Patient", "\n".join(contents.values()))
        self.assertNotIn("Doctor", "\n".join(contents.values()))

        backend = BackendGenerator()._build_backend_files(prompt)
        routes = next(file.content for file in backend if file.path.endswith("/routers/routes.py"))
        self.assertIn("counts['total'] = sum(counts.values())", routes)
        self.assertRegex(routes, r"db\.query\(\w+\)\.count\(\)")


if __name__ == "__main__":
    unittest.main()
