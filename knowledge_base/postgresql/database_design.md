# PostgreSQL — Database Design

Relational database design guidance for generated backends.

## Normalisation basics

- **1NF**: atomic values; no repeating groups.
- **2NF**: no partial dependencies on a composite key.
- **3NF**: no transitive dependencies on non-key attributes.
Normalise to remove redundancy; denormalise deliberately only for real query performance.

## Primary and foreign keys

- Every table should have a primary key (typically a surrogate `id SERIAL PRIMARY KEY` or a
  natural key when stable and unique).
- Use foreign keys to enforce referential integrity and relationships.
- Add `ON DELETE CASCADE` or `SET NULL` deliberately, matching business rules.

## Common column types

- Integer/bigint for ids and counts.
- `VARCHAR(n)` for short strings; `TEXT` for longer text.
- `NUMERIC`/`DECIMAL` for money (avoid float).
- `TIMESTAMP`/`DATE` for dates and times.
- `BOOLEAN` for flags.
- `JSONB` for flexible, semi-structured data.

## Relationships

- **One-to-many**: child table holds the `parent_id` foreign key.
- **Many-to-many**: junction/associative table with two foreign keys.
- **One-to-one**: share the primary key or place a unique FK.

## Naming conventions

- Tables: plural `snake_case` (`users`, `appointments`).
- Columns: `snake_case` (`full_name`, `created_at`).
- Junction tables: e.g. `user_roles`.

## Timestamps

Add `created_at` and `updated_at` columns where auditing is useful, with defaults.

## Constraints

- Add `NOT NULL`, `UNIQUE`, `CHECK` constraints to protect data integrity.
- Use `CHECK` for enums-lite values where a fixed set applies.
