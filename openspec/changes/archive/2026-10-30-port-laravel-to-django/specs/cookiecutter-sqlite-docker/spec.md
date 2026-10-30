## Purpose

Provides a production-ready Cookiecutter Django application scaffold in the repository root configured to run in local and production Docker containers using a persistent, WAL-enabled SQLite database and persistent media storage.

## ADDED Requirements

### Requirement: Root-level Cookiecutter Django project structure
The system SHALL locate the Django project files (`manage.py`, `pyproject.toml`, `config/`, `web_result/`, `compose/`, `docker-compose.local.yml`, and `docker-compose.production.yml`) directly in the repository root alongside `./old`.

#### Scenario: Project structure verification
- **WHEN** an operator inspects the repository root
- **THEN** `manage.py`, `docker-compose.local.yml`, `docker-compose.production.yml`, `config/`, and `web_result/` exist at the root level without modifying `./old`

### Requirement: SQLite database with WAL concurrency configuration
The system SHALL use SQLite as its default database engine in both local and production configurations, storing the database file in a dedicated persistent directory (`data/db.sqlite3` or `/app/data/db.sqlite3` in Docker) with Write-Ahead Logging (`journal_mode=WAL`), `foreign_keys=ON`, `synchronous=NORMAL`, and `IMMEDIATE` transaction mode enabled.

#### Scenario: SQLite database connection initialization
- **WHEN** the application opens a database connection
- **THEN** the connection uses `django.db.backends.sqlite3` with `journal_mode=WAL` and `foreign_keys=ON`

### Requirement: Docker Compose execution without PostgreSQL dependency
The system SHALL run via `docker-compose.local.yml` and `docker-compose.production.yml` without requiring a PostgreSQL container, mounting persistent volumes for the SQLite database directory (`/app/data`) and uploaded media files (`/app/web_result/media`).

#### Scenario: Container startup and persistence
- **WHEN** the Docker stack starts using `docker-compose.local.yml` or `docker-compose.production.yml`
- **THEN** the entrypoint initializes `/app/data` without waiting for PostgreSQL and preserves SQLite data and uploaded media across container restarts
