"""Database generation agent for creating domain-specific database blueprints."""

from __future__ import annotations

import re
from typing import Any

from .base_agent import BaseAgent
from .database_schema import DatabaseBlueprint, DatabaseTable, DatabaseColumn
from ..code_generator.website_spec import detect_website_key, PROJECT_TYPE_MODULES


class DatabaseGenerationAgent(BaseAgent):
    """Agent that creates domain-specific database blueprints from project requirements."""

    def __init__(self, name: str = "database_generation_agent") -> None:
        """Initialize the database generation agent."""
        super().__init__(name=name, description="Generates domain-specific database blueprints from project requirements")

    def analyze(self, user_prompt: str) -> Any:
        """Analyze a user prompt and return the input as-is."""
        return user_prompt

    def generate(self, requirements: Any) -> DatabaseBlueprint:
        """Generate a dynamic, domain-driven database blueprint from the provided requirements."""
        database_type = getattr(requirements, "database", "PostgreSQL / SQLite") or "PostgreSQL / SQLite"
        language = getattr(requirements, "language", "en") or "en"
        project_name = getattr(requirements, "project_name", "") or ""

        domain_context = " ".join(
            [
                project_name,
                str(getattr(requirements, "domain", "") or ""),
                str(getattr(requirements, "purpose", "") or ""),
                " ".join(str(item) for item in (getattr(requirements, "modules", None) or [])),
                " ".join(str(item) for item in (getattr(requirements, "data_requirements", None) or [])),
            ]
        )
        domain_key = detect_website_key(domain_context)

        domain_blueprints: dict[str, dict[str, Any]] = {
            "hospital": {
                "entities": ["User", "Doctor", "Patient", "Appointment", "Department", "Billing"],
                "tables": ["users", "doctors", "patients", "appointments", "departments", "billings"],
                "relationships": [
                    "Users -> Roles (N:1)",
                    "Departments -> Doctors (1:N)",
                    "Doctors -> Appointments (1:N)",
                    "Patients -> Appointments (1:N)",
                    "Patients -> Billings (1:N)",
                ],
                "indexes": ["users_email_idx", "appointments_date_idx", "patients_phone_idx", "doctors_specialty_idx"],
            },
            "ecommerce": {
                "entities": ["User", "Customer", "Category", "Product", "Order", "CartItem"],
                "tables": ["users", "customers", "categories", "products", "orders", "cart_items"],
                "relationships": [
                    "Categories -> Products (1:N)",
                    "Customers -> Orders (1:N)",
                    "Orders -> CartItems (1:N)",
                    "Products -> CartItems (1:N)",
                ],
                "indexes": ["users_email_idx", "products_category_idx", "orders_customer_idx", "products_sku_idx"],
            },
            "food_delivery": {
                "entities": ["User", "Restaurant", "MenuItem", "Customer", "Order", "Rider"],
                "tables": ["users", "restaurants", "menu_items", "customers", "orders", "riders"],
                "relationships": [
                    "Restaurants -> MenuItems (1:N)",
                    "Customers -> Orders (1:N)",
                    "Restaurants -> Orders (1:N)",
                    "Riders -> Orders (1:N)",
                ],
                "indexes": ["users_email_idx", "menu_items_restaurant_idx", "orders_status_idx", "restaurants_city_idx"],
            },
            "education": {
                "entities": ["User", "Department", "Faculty", "Course", "Student", "Attendance"],
                "tables": ["users", "departments", "faculty", "courses", "students", "attendances"],
                "relationships": [
                    "Departments -> Courses (1:N)",
                    "Faculty -> Courses (1:N)",
                    "Courses -> Students (N:M)",
                    "Students -> Attendances (1:N)",
                ],
                "indexes": ["users_email_idx", "courses_code_idx", "students_roll_number_idx"],
            },
            "finance": {
                "entities": ["User", "Customer", "Account", "Transaction", "Loan", "Card"],
                "tables": ["users", "customers", "accounts", "transactions", "loans", "cards"],
                "relationships": [
                    "Customers -> Accounts (1:N)",
                    "Accounts -> Transactions (1:N)",
                    "Customers -> Loans (1:N)",
                    "Accounts -> Cards (1:N)",
                ],
                "indexes": ["users_email_idx", "accounts_number_idx", "transactions_date_idx"],
            },
            "inventory": {
                "entities": ["User", "Supplier", "Category", "Product", "Warehouse", "Shipment"],
                "tables": ["users", "suppliers", "categories", "products", "warehouses", "shipments"],
                "relationships": [
                    "Categories -> Products (1:N)",
                    "Suppliers -> Products (1:N)",
                    "Warehouses -> Shipments (1:N)",
                    "Products -> Shipments (1:N)",
                ],
                "indexes": ["users_email_idx", "products_sku_idx", "shipments_tracking_idx"],
            },
            "real_estate": {
                "entities": ["User", "Agent", "Client", "Property", "Listing", "Booking"],
                "tables": ["users", "agents", "clients", "properties", "listings", "bookings"],
                "relationships": [
                    "Agents -> Listings (1:N)",
                    "Properties -> Listings (1:1)",
                    "Clients -> Bookings (1:N)",
                    "Listings -> Bookings (1:N)",
                ],
                "indexes": ["users_email_idx", "properties_location_idx", "listings_price_idx"],
            },
            "hospitality": {
                "entities": ["User", "Guest", "Room", "Booking", "Staff", "Service"],
                "tables": ["users", "guests", "rooms", "bookings", "staffs", "services"],
                "relationships": [
                    "Guests -> Bookings (1:N)",
                    "Rooms -> Bookings (1:N)",
                    "Staffs -> Services (1:N)",
                ],
                "indexes": ["users_email_idx", "rooms_number_idx", "bookings_dates_idx"],
            },
            "railway": {
                "entities": ["User", "Train", "Route", "Station", "Booking", "Schedule"],
                "tables": ["users", "trains", "routes", "stations", "bookings", "schedules"],
                "relationships": [
                    "Routes -> Trains (1:N)",
                    "Stations -> Schedules (1:N)",
                    "Trains -> Schedules (1:N)",
                    "Users -> Bookings (1:N)",
                    "Trains -> Bookings (1:N)",
                ],
                "indexes": ["users_email_idx", "trains_number_idx", "routes_name_idx", "schedules_departure_idx"],
            },
            "travel": {
                "entities": ["User", "Traveler", "Destination", "Package", "Booking", "Hotel"],
                "tables": ["users", "travelers", "destinations", "packages", "bookings", "hotels"],
                "relationships": [
                    "Destinations -> Packages (1:N)",
                    "Travelers -> Bookings (1:N)",
                    "Packages -> Bookings (1:N)",
                ],
                "indexes": ["users_email_idx", "packages_destination_idx", "bookings_date_idx"],
            },
            "fitness": {
                "entities": ["User", "Member", "Plan", "Trainer", "Class", "Attendance"],
                "tables": ["users", "members", "plans", "trainers", "classes", "attendances"],
                "relationships": [
                    "Plans -> Members (1:N)",
                    "Trainers -> Classes (1:N)",
                    "Members -> Attendances (1:N)",
                    "Classes -> Attendances (1:N)",
                ],
                "indexes": ["users_email_idx", "members_phone_idx", "classes_schedule_idx"],
            },
            "task": {
                "entities": ["User", "Project", "Task", "Comment", "Tag", "Attachment"],
                "tables": ["users", "projects", "tasks", "comments", "tags", "attachments"],
                "relationships": [
                    "Users -> Projects (1:N)",
                    "Projects -> Tasks (1:N)",
                    "Tasks -> Comments (1:N)",
                    "Tasks -> Attachments (1:N)",
                ],
                "indexes": ["users_email_idx", "tasks_project_idx", "tasks_status_idx"],
            },
            "generic": {
                "entities": ["User", "Role", "Item", "Category", "Record", "ActivityLog"],
                "tables": ["users", "roles", "items", "categories", "records", "activity_logs"],
                "relationships": [
                    "Users -> Roles (N:1)",
                    "Categories -> Items (1:N)",
                    "Users -> Records (1:N)",
                    "Users -> ActivityLogs (1:N)",
                ],
                "indexes": ["users_email_idx", "records_created_idx", "items_category_idx"],
            },
        }

        bp = domain_blueprints.get(domain_key, domain_blueprints["generic"])
        entities = bp["entities"]
        tables = bp["tables"]
        relationships = bp["relationships"]
        indexes = bp["indexes"]

        table_details: list[DatabaseTable] = []
        for entity, table_name in zip(entities, tables):
            columns = [
                DatabaseColumn(name="id", data_type="Integer", primary_key=True, nullable=False),
                DatabaseColumn(name="name" if entity != "User" else "username", data_type="String", nullable=False),
                DatabaseColumn(name="status", data_type="String", default="Active"),
                DatabaseColumn(name="created_at", data_type="DateTime", nullable=False),
                DatabaseColumn(name="updated_at", data_type="DateTime", nullable=True),
            ]
            if entity == "User":
                columns.insert(2, DatabaseColumn(name="email", data_type="String", unique=True, nullable=False))
                columns.insert(3, DatabaseColumn(name="hashed_password", data_type="String", nullable=False))

            table_details.append(
                DatabaseTable(
                    name=table_name,
                    model_name=entity,
                    columns=columns,
                    foreign_keys=[],
                )
            )

        seed_records = [f"Initial {e} demo dataset" for e in entities[:4]]

        return DatabaseBlueprint(
            database_type=database_type,
            tables=tables,
            relationships=relationships,
            indexes=indexes,
            language=language,
            entities=entities,
            table_details=table_details,
            seed_records=seed_records,
        )
