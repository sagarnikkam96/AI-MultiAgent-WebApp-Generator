# Demonstration — Hospital Management System

A safe, illustrative example used to show how the knowledge base provides technical context
to the multi-agent pipeline.

> ⚠️ **IMPORTANT**
> This example is a **synthetic demonstration** for illustrating how technical knowledge maps
> to software generation. It contains **no real patient data** — no real names, medical
> records, phone numbers, addresses, or other sensitive information. Do **not** treat any of
> the sample fields below as a real dataset.

## Example USER REQUIREMENT

> "Build a hospital management system using React, FastAPI and PostgreSQL."

## Relevant technical knowledge (from this knowledge base)

| Requested area    | Knowledge base source                       | Technical context provided          |
| ----------------- | ------------------------------------------- | ----------------------------------- |
| React             | `react/components.md`, `react/state_management.md` | Component model, props, state hooks |
| FastAPI           | `fastapi/api_design.md`, `fastapi/routing.md`       | REST endpoints, routers, schemas    |
| PostgreSQL        | `postgresql/database_design.md`                     | Tables, relations, keys             |
| SQLAlchemy        | `sqlalchemy/models.md`, `sqlalchemy/sessions.md`    | ORM models, sessions                |
| Authentication    | `authentication/jwt.md`, `authentication/authorization.md` | JWT + role-based access   |
| REST API          | `rest_api/principles.md`, `rest_api/endpoints.md`   | Resource endpoints, status codes    |
| Architecture      | `architecture/*.md`                                  | Layered backend + frontend layout   |
| Security          | `security/*.md`                                      | CORS, validation, API security      |

## How the technical context supports the agents

**Requirement Analysis** maps the prompt to structured requirements:
- Frontend: React
- Backend: FastAPI
- Database: PostgreSQL
- Authentication: JWT login
- Modules: Login, Dashboard, Patients, Doctors, Appointments, Billing

**Planning Agent** uses the knowledge base to derive tasks:
- Frontend tasks: create React project, configure routing, build components, API integration
- Backend tasks: create API, authentication, business logic
- Database tasks: design tables, relationships, seed data

**Backend Agent** uses `fastapi/*` and `rest_api/*` to generate:
- Routers for `/auth/login`, `/patients`, `/doctors`, `/appointments`
- Pydantic schemas for request/response validation
- JWT authentication and role-based authorization

**Database Agent** uses `postgresql/*` and `sqlalchemy/*` to generate:
- Tables: `users`, `patients`, `doctors`, `appointments`, `bills`
- Foreign-key relationships (patient ↔ appointments, doctor ↔ appointments)
- SQLAlchemy models and session handling

**Frontend Generator** uses `react/*`, `typescript/*`, `vite/*` to generate:
- A typed React + TypeScript + Vite app
- Components: Login, Dashboard, Patients, Doctors, Appointments
- An API service layer calling the generated FastAPI endpoints

## Illustrative (synthetic) schema sketch — NOT real data

```sql
CREATE TABLE patients (
    id        SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    dob       DATE,
    condition VARCHAR(255)
);

CREATE TABLE doctors (
    id         SERIAL PRIMARY KEY,
    full_name  VARCHAR(120) NOT NULL,
    specialty  VARCHAR(120)
);

CREATE TABLE appointments (
    id         SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    doctor_id  INTEGER NOT NULL REFERENCES doctors(id),
    slot       TIMESTAMP NOT NULL
);
```

These are **placeholder** column examples for demonstration only. No actual patient records
are stored or claimed.

## Why this mapping matters

The knowledge base lets the pipeline answer "what should this app look like technically?" in
a consistent, grounded way, so every generated hospital-management app uses the same sound
stack conventions (typed React, well-structured FastAPI routers, normalised PostgreSQL,
JWT auth) instead of ad-hoc guesses.
