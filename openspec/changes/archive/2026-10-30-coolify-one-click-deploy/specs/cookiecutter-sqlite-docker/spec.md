## MODIFIED Requirements

### Requirement: Root-level Cookiecutter Django project structure
The system SHALL locate the Django project files (`manage.py`, `pyproject.toml`, `config/`, `web_result/`, `compose/`, `docker-compose.yaml`, `docker-compose.local.yml`, and `docker-compose.production.yml`) directly in the repository root alongside `./old`.

#### Scenario: Project structure verification
- **WHEN** an operator inspects the repository root
- **THEN** `manage.py`, `docker-compose.yaml`, `docker-compose.local.yml`, `docker-compose.production.yml`, `config/`, and `web_result/` exist at the root level without modifying `./old`

### Requirement: Docker Compose execution without PostgreSQL dependency
The system SHALL run via `docker-compose.local.yml`, `docker-compose.production.yml`, and `docker-compose.yaml` without requiring PostgreSQL, `traefik`, or `nginx` containers in production, mounting persistent volumes for the SQLite database directory (`/app/data`), uploaded media files (`/app/web_result/media`), and backup archives (`/app/backups`).

#### Scenario: Container startup and persistence
- **WHEN** the Docker stack starts using `docker-compose.local.yml`, `docker-compose.production.yml`, or `docker-compose.yaml`
- **THEN** the entrypoint initializes `/app/data`, `/app/web_result/media`, and `/app/backups` without waiting for PostgreSQL and preserves SQLite data, uploaded media, and backups across container restarts
