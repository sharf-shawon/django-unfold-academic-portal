# coolify-one-click-deployment Specification

## Purpose

Provides zero-configuration one-click deployment on Coolify using `/docker-compose.yaml` auto-detection, Coolify magic environment variables for automatic domain routing and secret generation, container health checks, first-boot legacy data seeding, and automated WAL-safe SQLite + media backups.

## Requirements

### Requirement: Coolify auto-detected root Docker Compose and environment template
The system SHALL provide a `/docker-compose.yaml` file and a `/.env.example` file at the repository root so Coolify's Smart Scan (`RepositoryDetector`) and default `docker_compose_location` (`/docker-compose.yaml`) automatically detect the Docker Compose build pack and environment variables without manual configuration. The `/docker-compose.yaml` file SHALL define only the `django` service (omitting `traefik` and `nginx`) and SHALL NOT hardcode an `image:` name so Coolify can inject commit-based image tags for rollbacks.

#### Scenario: Coolify repository auto-detection
- **WHEN** a user adds the repository to Coolify as a Git-based Application
- **THEN** Coolify locates `/docker-compose.yaml` at the root with a single `django` service and no `traefik` or `nginx` services

### Requirement: Coolify magic environment variables and dynamic domain/CSRF configuration
The system SHALL declare `SERVICE_FQDN_DJANGO_5000` and `SERVICE_BASE64_64_DJANGO` in `/docker-compose.yaml` so Coolify automatically assigns a domain routed to internal container port `5000` and generates a persistent 64-character `DJANGO_SECRET_KEY`. The production settings module (`config/settings/production.py`) SHALL dynamically include hostnames and URLs from `COOLIFY_FQDN`, `COOLIFY_URL`, `SERVICE_FQDN_DJANGO`, `SERVICE_FQDN_DJANGO_5000`, `SERVICE_URL_DJANGO`, and `SERVICE_URL_DJANGO_5000` in `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.

#### Scenario: Dynamic Coolify domain and CSRF origin resolution
- **WHEN** Coolify injects `SERVICE_FQDN_DJANGO=results.example.com`, `SERVICE_FQDN_DJANGO_5000=results.example.com:5000`, and `SERVICE_URL_DJANGO=https://results.example.com`
- **THEN** `ALLOWED_HOSTS` contains `results.example.com`, `localhost`, and `127.0.0.1` (without port suffixes) and `CSRF_TRUSTED_ORIGINS` contains `https://results.example.com`

### Requirement: Coolify-compatible container health check endpoint
The system SHALL expose a `/healthz/` HTTP endpoint that verifies SQLite database connectivity (`SELECT 1`) and returns HTTP `200 OK` with JSON `{"status": "ok", "database": "ok"}`, exempt from `SECURE_SSL_REDIRECT`. Both `compose/production/django/Dockerfile` and `/docker-compose.yaml` SHALL define a health check probing `http://127.0.0.1:5000/healthz/` using `curl`.

#### Scenario: Container health probe over plain internal HTTP
- **WHEN** the Docker healthcheck requests `GET http://127.0.0.1:5000/healthz/` even with `DJANGO_SECURE_SSL_REDIRECT=True`
- **THEN** the application executes a database check and returns HTTP `200 OK` with `{"status": "ok", "database": "ok"}` instead of a `301` redirect

### Requirement: First-boot automatic legacy seeding and WAL-safe automated backups
The system SHALL mount Coolify-managed persistent volumes for `/app/data`, `/app/web_result/media`, and `/app/backups`. On first boot when the SQLite database has zero `Student` records and `DJANGO_AUTO_IMPORT_LEGACY=True`, `/start` SHALL automatically import `/app/old/database/Result.sql`, copy `/app/old/public/uploads/images`, and seed the admin/demo user. The system SHALL also provide a `python manage.py backup_data` command that uses Python's online `sqlite3.Connection.backup()` API to create consistent `.tar.gz` archives of the SQLite database and media files in `/app/backups` with retention pruning (`--keep`) and `--restore` support, invoked automatically before migrations on container startup (`DJANGO_AUTO_BACKUP_ON_START=True`) and periodically (`DJANGO_AUTO_BACKUP_INTERVAL`).

#### Scenario: Online backup and restore of SQLite database and media files
- **WHEN** `python manage.py backup_data` is executed
- **THEN** the command creates a timestamped `.tar.gz` archive in the backup directory containing an atomic SQLite backup (`db.sqlite3`) and uploaded media files, prunes older archives beyond the retention limit, and can restore the database and media files via `python manage.py backup_data --restore <archive>`
