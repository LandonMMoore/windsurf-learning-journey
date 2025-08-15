# Alembic Deep Dive Guide

## Introduction
Alembic is a lightweight database migration tool for SQLAlchemy. It helps manage schema changes over time, ensuring consistency in database structures across different environments.

## 1. Installing Alembic
Alembic is included in most FastAPI projects using SQLAlchemy. If not installed, you can add it using Poetry:

```sh
poetry add alembic
```

Verify the installation:

```sh
alembic --version
```

## 2. Initializing Alembic
To set up Alembic in your project, navigate to your FastAPI project directory and run:

```sh
alembic init alembic
```

This creates an `alembic/` directory with necessary configurations.

## 3. Configuring Alembic
Edit the `alembic.ini` file to set the database connection URL:

```ini
sqlalchemy.url = postgresql://user:password@localhost/dbname
```

For a FastAPI project using environment variables, modify `alembic/env.py`:

```python
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.declarative import declarative_base
from myproject.database import Base  # Import your SQLAlchemy Base

target_metadata = Base.metadata
```

## 4. Creating Migrations
To generate a new migration file based on model changes, run:

```sh
alembic revision --autogenerate -m "Migration message"
```

This scans your models and generates a migration file under `alembic/versions/`.

## 5. Applying Migrations
To apply pending migrations and update the database schema:

```sh
alembic upgrade head
```

To apply a specific migration revision:

```sh
alembic upgrade <revision_id>
```

## 6. Rolling Back Migrations
If a migration needs to be undone, rollback to the previous state:

```sh
alembic downgrade -1
```

To rollback multiple steps:

```sh
alembic downgrade <revision_id>
```

## 7. Deleting and Recreating Tables
If a table structure needs modification but migration scripts are failing, use the following steps:

1. **Delete the table manually:**

```sql
DROP TABLE table_name CASCADE;
```

2. **Create a new migration:**

```sh
alembic revision --autogenerate -m "Recreate table_name"
```

3. **Apply the new migration:**

```sh
alembic upgrade head
```

## 8. Viewing Migration History
To see all applied migrations:

```sh
alembic history
```

To check the current migration applied to the database:

```sh
alembic current
```

## 9. Stamping the Database
If the database schema is manually changed and migrations need to sync without running them, stamp it:

```sh
alembic stamp head
```

## 10. Handling Migration Conflicts
If multiple developers work on migrations, conflicts can occur. Use the following:

```sh
alembic merge <revision1> <revision2> -m "Merge conflicts"
```

This creates a new migration file merging both revisions.

## 11. Resetting Migrations
If migrations get out of sync, you may need to reset:

```sh
alembic downgrade base
rm -rf alembic/versions/*
alembic revision --autogenerate -m "Reset migrations"
alembic upgrade head
```

## 12. Best Practices
- Always commit migrations to version control.
- Use `--autogenerate` but **review** changes before applying.
- Avoid deleting migration files unless necessary.
- Keep `alembic.ini` database settings consistent across environments.

---

