# cookiecutter-sqlite-docker Specification

## Purpose

Provides a production-ready Cookiecutter Django application scaffold in the repository root configured to run in local and production Docker containers using a persistent, WAL-enabled SQLite database and persistent media storage.

## Requirements

### Requirement: Root-level Cookiecutter Django project structure
The system SHALL locate the Django project files (`manage.py`, `pyproject.toml`, `config/`, `web_result/`, `compose/`, `docker-compose.yaml`, `docker-compose.local.yml`, and `docker-compose.production.yml`) directly in the repository root alongside `./old`.

#### Scenario: Project structure verification
- **WHEN** an operator inspects the repository root
- **THEN** `manage.py`, `docker-compose.yaml`, `docker-compose.local.yml`, `docker-compose.production.yml`, `config/`, and `web_result/` exist at the root level without modifying `./old`

### Requirement: SQLite database with WAL concurrency configuration
The system SHALL use SQLite as its default database engine in both local and production configurations, storing the database file in a dedicated persistent directory (`data/db.sqlite3` or `/app/data/db.sqlite3` in Docker) with Write-Ahead Logging (`journal_mode=WAL`), `foreign_keys=ON`, `synchronous=NORMAL`, and `IMMEDIATE` transaction mode enabled.

#### Scenario: SQLite database connection initialization
- **WHEN** the application opens a database connection
- **THEN** the connection uses `django.db.backends.sqlite3` with `journal_mode=WAL` and `foreign_keys=ON`

### Requirement: Docker Compose execution without PostgreSQL dependency
The system SHALL run via `docker-compose.local.yml`, `docker-compose.production.yml`, and `docker-compose.yaml` without requiring PostgreSQL, `traefik`, or `nginx` containers in production, mounting persistent volumes for the SQLite database directory (`/app/data`), uploaded media files (`/app/web_result/media`), and backup archives (`/app/backups`).

#### Scenario: Container startup and persistence
- **WHEN** the Docker stack starts using `docker-compose.local.yml`, `docker-compose.production.yml`, or `docker-compose.yaml`
- **THEN** the entrypoint initializes `/app/data`, `/app/web_result/media`, and `/app/backups` without waiting for PostgreSQL and preserves SQLite data, uploaded media, and backups across container restarts
