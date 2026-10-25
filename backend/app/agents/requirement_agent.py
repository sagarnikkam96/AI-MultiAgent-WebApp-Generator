"""Deterministic and LLM-augmented requirement analysis agent."""

from __future__ import annotations

import json
import re
from typing import Any

from ..code_generator.website_spec import (
    derive_website_modules,
    derive_website_type_name,
    detect_website_key,
    WEBSITE_SPECS,
    PROJECT_TYPE_MODULES,
)
from .base_agent import BaseAgent
from .schemas import RequirementSchema


class RequirementAgent(BaseAgent):
    """Agent that extracts comprehensive structured requirements from a prompt."""

    def __init__(self, name: str = "requirement_agent") -> None:
        """Initialize the requirement agent."""
        super().__init__(name=name, description="Extracts structured requirements from a prompt")

    def analyze(self, user_prompt: str) -> RequirementSchema:
        """Analyze a user prompt and return a rich structured requirement schema."""
        prompt = (user_prompt or "").strip()
        lower_prompt = prompt.lower()

        project_name = self._extract_project_name(lower_prompt) or self._fallback_project_name(lower_prompt)
        project_type = self._detect_project_type(lower_prompt)
        frontend = self._detect_frontend(lower_prompt)
        backend = self._detect_backend(lower_prompt)
        database = self._detect_database(lower_prompt)
        authentication = self._detect_authentication(lower_prompt)
        modules = self._detect_modules(lower_prompt)
        language = self._detect_language(lower_prompt)

        domain_key = detect_website_key(lower_prompt)
        user_roles = self._derive_user_roles(domain_key, lower_prompt)
        features = self._derive_features(domain_key, modules, authentication)
        pages = ["Dashboard", *[m for m in modules if m not in ("Dashboard", "Admin")]]
        if authentication and "Login" not in pages:
            pages.insert(0, "Login")

        purpose = self._derive_purpose(project_name, project_type, domain_key, prompt)
        functional_requirements = self._derive_functional_requirements(domain_key, modules, authentication)
        data_requirements = self._derive_data_requirements(domain_key)
        constraints = [
            "FastAPI async REST endpoints with Pydantic request/response validation",
            "Responsive React 18 frontend with TypeScript and dark/light UI modes",
            "SQLAlchemy ORM models with parameterized query security",
            "Client-side and server-side input validation",
        ]

        validation_errors: list[str] = []
        if not frontend:
            validation_errors.append("Frontend technology not specified")
        if not backend:
            validation_errors.append("Backend technology not specified")
        if not project_name:
            validation_errors.append("Project name not detected")

        return RequirementSchema(
            project_name=project_name,
            project_type=project_type,
            frontend=frontend,
            backend=backend,
            database=database,
            authentication=authentication,
            modules=modules,
            validation_errors=validation_errors,
            language=language,
            purpose=purpose,
            domain=project_type,
            user_roles=user_roles,
            features=features,
            pages=pages,
            functional_requirements=functional_requirements,
            data_requirements=data_requirements,
            constraints=constraints,
        )

    def _extract_project_name(self, prompt: str) -> str:
        """Extract a project name using keyword matching."""
        if "project name" in prompt:
            extracted = prompt.split("project name", 1)[1].strip()
            for separator in (" for ", " is ", " called ", " using ", " with ", "\n"):
                if separator in extracted:
                    extracted = extracted.split(separator, 1)[0].strip()
                    break
            return self._clean_name(extracted)

        if "called" in prompt:
            extracted = prompt.split("called", 1)[1].strip()
            for separator in (" for ", " is ", " with ", "\n"):
                if separator in extracted:
                    extracted = extracted.split(separator, 1)[0].strip()
                    break
            return self._clean_name(extracted)

        for prefix in ("build a ", "create a ", "develop a ", "generate a ", "design a ", "build ", "create ", "develop "):
            if prompt.startswith(prefix):
                extracted = prompt[len(prefix):].strip()
                for separator in (" using ", " with ", " for ", " and ", "\n"):
                    if separator in extracted:
                        extracted = extracted.split(separator, 1)[0].strip()
                        break
                return self._clean_name(extracted)

        return ""

    def _fallback_project_name(self, prompt: str) -> str:
        """Derive a friendly project name when not explicitly detected."""
        domain_type = derive_website_type_name(prompt)
        if domain_type and domain_type != "General":
            return f"{domain_type} System"
        return "Full-Stack Application"

    def _clean_name(self, text: str) -> str:
        words = text.strip().split()
        if not words:
            return ""
        # Cap to 5 words and capitalize
        cleaned = " ".join(words[:5])
        return cleaned.title()

    def _detect_project_type(self, prompt: str) -> str:
        """Detect the project domain type from centralized website specs."""
        return derive_website_type_name(prompt)

    def _detect_frontend(self, prompt: str) -> str:
        """Detect a frontend technology from the prompt."""
        return "React"

    def _detect_backend(self, prompt: str) -> str:
        """Detect a backend technology from the prompt."""
        if "django" in prompt:
            return "Django"
        if "flask" in prompt:
            return "Flask"
        return "FastAPI"

    def _detect_database(self, prompt: str) -> str:
        """Detect a database technology from the prompt."""
        if "postgresql" in prompt or "postgres" in prompt:
            return "PostgreSQL"
        if "mysql" in prompt:
            return "MySQL"
        if "mongodb" in prompt:
            return "MongoDB"
        return "PostgreSQL / SQLite"

    def _detect_authentication(self, prompt: str) -> bool:
        """Determine whether authentication is required."""
        return any(keyword in prompt for keyword in ("auth", "authentication", "login", "signup", "jwt", "user", "role"))

    def _detect_modules(self, prompt: str) -> list[str]:
        """Detect module names for the prompt's website type."""
        modules = derive_website_modules(prompt)

        module_keywords: list[tuple[str, tuple[str, ...]]] = [
            ("Login", ("login", "auth", "signin")),
            ("Dashboard", ("dashboard", "metrics")),
            ("Admin", ("admin", "management")),
            ("Payments", ("payment", "pay", "checkout")),
            ("Reports", ("report", "analytics", "insights")),
            ("Inventory", ("inventory", "stock")),
            ("Settings", ("settings", "preferences")),
        ]

        for module_name, keywords in module_keywords:
            if any(keyword in prompt for keyword in keywords) and module_name not in modules:
                modules.append(module_name)

        return modules

    def _detect_language(self, prompt: str) -> str:
        """Detect the requested output language from the prompt."""
        language_hints: dict[str, tuple[str, ...]] = {
            "hi": ("hindi", "हिंदी", "हिन्दी", "in hindi"),
            "kn": ("kannada", "ಕನ್ನಡ", "in kannada"),
            "mr": ("marathi", "मराठी", "in marathi"),
            "te": ("telugu", "తెలుగు", "in telugu"),
            "bn": ("bengali", "বাংলা", "in bengali"),
            "ta": ("tamil", "தமிழ்", "in tamil"),
            "gu": ("gujarati", "ગુજરાતી", "in gujarati"),
            "ml": ("malayalam", "മലയാളം", "in malayalam"),
            "pa": ("punjabi", "ਪੰਜਾਬੀ", "in punjabi"),
            "or": ("odia", "oriya", "ଓଡ଼ିଆ", "in odia"),
            "as": ("assamese", "অসমীয়া", "in assamese"),
            "ur": ("urdu", "اردو", "in urdu"),
            "sa": ("sanskrit", "संस्कृतम्", "in sanskrit"),
            "ne": ("nepali", "नेपाली", "in nepali"),
            "kok": ("konkani", "कोंकणी", "in konkani"),
            "sd": ("sindhi", "سنڌي", "in sindhi"),
            "ks": ("kashmiri", "کٲشُر", "in kashmiri"),
            "mni": ("manipuri", "meitei", "মৈতৈলোন্", "in manipuri"),
            "mai": ("maithili", "मैथिली", "in maithili"),
        }
        lower_prompt = prompt.lower()
        for code, hints in language_hints.items():
            if any(hint in lower_prompt for hint in hints):
                return code
        return "en"

    def _derive_user_roles(self, domain_key: str, prompt: str) -> list[str]:
        role_map: dict[str, list[str]] = {
            "hospital": ["Administrator", "Doctor", "Patient", "Nurse", "Billing Staff"],
            "ecommerce": ["Customer", "Store Admin", "Inventory Manager", "Support Agent"],
            "food_delivery": ["Customer", "Restaurant Owner", "Delivery Rider", "Admin"],
            "education": ["Student", "Instructor", "Department Head", "Administrator"],
            "finance": ["Account Holder", "Branch Manager", "Loan Officer", "Auditor"],
            "inventory": ["Warehouse Manager", "Supplier", "Stock Supervisor", "Auditor"],
            "real_estate": ["Property Buyer", "Listing Agent", "Property Owner", "Broker"],
            "hospitality": ["Guest", "Front Desk Receptionist", "Hotel Manager", "Housekeeping"],
            "railway": ["Rail Operations Manager", "Station Master", "Train Dispatcher", "Passenger"],
            "travel": ["Traveler", "Tour Operator", "Travel Agent", "Booking Admin"],
            "fitness": ["Gym Member", "Personal Trainer", "Fitness Instructor", "Club Manager"],
            "task": ["Project Owner", "Team Lead", "Developer", "Collaborator"],
            "generic": ["Administrator", "Standard User", "Guest"],
        }
        return role_map.get(domain_key, ["Administrator", "Standard User"])

    def _derive_features(self, domain_key: str, modules: list[str], auth: bool) -> list[str]:
        features = [
            f"Interactive {domain_key.replace('_', ' ').title()} Dashboard with Real-Time KPIs",
            "Complete user-interface localization in the selected output language",
            "Dynamic CRUD Management for Domain Records",
            "Instant Search, Filters, and Table Pagination",
            "RESTful API Integration with FastAPI Backend",
        ]
        if auth:
            features.insert(1, "Secure Authentication with JWT Tokens & Role-Based Permissions")
        for m in modules[:3]:
            if m not in ("Dashboard", "Login"):
                features.append(f"Dedicated {m} Workflow and Record Inspection")
        return features

    def _derive_purpose(self, project_name: str, project_type: str, domain_key: str, raw_prompt: str) -> str:
        purposes: dict[str, str] = {
            "hospital": f"Provide an autonomous healthcare management platform for patient admissions, doctor schedules, appointments, and billing.",
            "ecommerce": f"Deliver a high-converting digital storefront for product catalog browsing, cart operations, order processing, and customer management.",
            "food_delivery": f"Facilitate seamless food ordering, restaurant menu administration, order tracking, and rider coordination.",
            "education": f"Streamline academic operations, student enrollments, course catalogs, faculty assignments, and attendance records.",
            "finance": f"Manage banking accounts, financial transactions, loan applications, customer profiles, and ledger statements securely.",
            "inventory": f"Optimize supply chain operations with real-time stock levels, supplier records, shipment tracking, and warehouse management.",
            "real_estate": f"Showcase real estate properties, connect buyers with licensed agents, manage property listings, and schedule client viewings.",
            "hospitality": f"Handle hotel reservations, guest check-ins, room inventory availability, and housekeeping services.",
            "railway": "Coordinate train fleets, routes, stations, schedules, passenger bookings, and railway operations.",
            "travel": f"Offer curated holiday tour packages, destination guides, traveler bookings, and itinerary management.",
            "fitness": f"Manage gym membership plans, class schedules, personal trainer sessions, and member attendance tracking.",
            "task": f"Coordinate team projects, task boards, deadlines, priorities, and collaborator assignments.",
            "generic": f"Provide a complete full-stack web application for {raw_prompt or project_name}.",
        }
        return purposes.get(domain_key, f"Full-stack web application engineered for {project_name}.")

    def _derive_functional_requirements(self, domain_key: str, modules: list[str], auth: bool) -> list[str]:
        reqs = [
            "Provide asynchronous REST API endpoints with status codes and Pydantic schemas",
            "Enable persistent data storage using SQLAlchemy ORM models with SQLite and PostgreSQL compatibility",
            "Render responsive single page application in React 18 with modular components",
            "Support instant create, read, update, and delete actions for primary domain entities",
        ]
        if auth:
            reqs.append("Authenticate users with encrypted password hashing and JWT access tokens")
        reqs.append(f"Organize navigation hierarchy across: {', '.join(modules)}")
        return reqs

    def _derive_data_requirements(self, domain_key: str) -> list[str]:
        entity_map: dict[str, list[str]] = {
            "hospital": ["Patient", "Doctor", "Appointment", "Department", "BillingRecord"],
            "ecommerce": ["Product", "Category", "Customer", "Order", "CartItem"],
            "food_delivery": ["Restaurant", "MenuItem", "Customer", "Order", "Rider"],
            "education": ["Student", "Course", "Faculty", "Attendance", "Department"],
            "finance": ["Account", "Transaction", "Loan", "Customer", "Branch"],
            "inventory": ["Item", "Category", "Supplier", "Shipment", "Warehouse"],
            "real_estate": ["Property", "Listing", "Agent", "Client", "Booking"],
            "hospitality": ["Room", "Booking", "Guest", "Staff", "Service"],
            "railway": ["Train", "Route", "Station", "Schedule", "Booking"],
            "travel": ["Package", "Destination", "Booking", "Traveler", "Hotel"],
            "fitness": ["Member", "Plan", "Trainer", "Class", "Attendance"],
            "task": ["Project", "Task", "User", "Comment", "Tag"],
            "generic": ["Item", "Category", "Record", "Report", "User"],
        }
        return entity_map.get(domain_key, ["Item", "Record", "User"])
