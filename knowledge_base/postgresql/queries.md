# PostgreSQL — Queries

Common SQL patterns for generated backends backed by PostgreSQL.

## Basic CRUD

```sql
-- Create
INSERT INTO users (email, name) VALUES ('a@example.com', 'Alice') RETURNING id;

-- Read
SELECT id, email, name FROM users WHERE id = 1;

-- Update
UPDATE users SET name = 'Alicia' WHERE id = 1;

-- Delete
DELETE FROM users WHERE id = 1;
```

## Filtering and ordering

```sql
SELECT id, name FROM products
WHERE category_id = 3 AND price > 10
ORDER BY price DESC
LIMIT 20 OFFSET 0;
```

## Joins

```sql
SELECT u.name, o.total
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE u.id = 1;
```

## Aggregation

```sql
SELECT category_id, COUNT(*) AS cnt, SUM(price) AS total
FROM products
GROUP BY category_id
HAVING COUNT(*) > 5;
```

## Relationships via foreign keys

Use `JOIN` (or the ORM's relationship API) to traverse foreign-key relationships instead of
manual multi-query lookups.

## Parameterisation

Always use **parameterised queries** (or the ORM) — never interpolate user input directly
into SQL. This prevents SQL injection. With SQLAlchemy core/text, use `:` bind params.

```sql
SELECT * FROM users WHERE email = :email;
```

## Indexing

- Create indexes on columns used frequently in `WHERE`/`JOIN`/`ORDER BY`.
- Avoid over-indexing: each index adds write cost. Index foreign keys used in joins.

## Transactions

Wrap multi-step writes in a transaction so they commit atomically and can be rolled back on
error. The ORM session commit/rollback handles this.
