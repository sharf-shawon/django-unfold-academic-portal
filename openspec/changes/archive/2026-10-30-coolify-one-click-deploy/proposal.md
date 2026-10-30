## Why

Deploying the application to Coolify currently requires manual configuration of the Docker Compose file location, removal of redundant reverse-proxy containers (`traefik` and `nginx`), manual setup of secret keys and `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` for generated domains, manual health-check wiring, and manual database/media backup management. Providing a Coolify-native `/docker-compose.yaml` with magic environment variables, health checks, first-boot seeding, and automated online SQLite + media backups enables true zero-configuration one-click deployment on Coolify.

## What Changes

- **Add root `/docker-compose.yaml` (and update `/docker-compose.production.yml`) for Coolify auto-detection**:
  - Place `/docker-compose.yaml` at the repository root so Coolify's default `docker_compose_location` (`/docker-compose.yaml`) and Smart Scan (`RepositoryDetector`) automatically select the Docker Compose build pack without customization.
  - Add `.env.example` at the repository root so Coolify's Smart Scan detects and documents all optional environment variables.
  - Remove the redundant `traefik` and `nginx` services from the production Docker Compose files since Coolify provides its own Traefik reverse proxy and Django directly serves `/static/` (via WhiteNoise) and `/uploads/` + `/media/` (`DJANGO_SERVE_MEDIA=True`).
  - Omit a hardcoded `image:` tag on the `django` service so Coolify injects commit-based image tags (`{uuid}_django:{commit}`) for one-click rollbacks.
- **Configure Coolify magic environment variables and dynamic domain/CSRF discovery**:
  - Declare `SERVICE_FQDN_DJANGO_5000` on the `django` service so Coolify automatically generates/assigns a domain and routes its Traefik proxy to internal container port `5000`.
  - Declare `DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY:-${SERVICE_BASE64_64_DJANGO}}` and `DJANGO_ADMIN_PASSWORD=${DJANGO_ADMIN_PASSWORD:-${SERVICE_PASSWORD_ADMIN}}` using Coolify's single-token magic secret generators.
  - Update `config/settings/production.py` to dynamically populate `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` from `COOLIFY_FQDN`, `COOLIFY_URL`, `SERVICE_FQDN_DJANGO`, `SERVICE_FQDN_DJANGO_5000`, `SERVICE_URL_DJANGO`, and `SERVICE_URL_DJANGO_5000` (stripping port suffixes and schemes as appropriate) and to exempt `/healthz/` from `SECURE_SSL_REDIRECT`.
- **Add Coolify-compatible Docker health checks**:
  - Add a `/healthz/` endpoint (`HealthCheckView`) that executes a SQLite `SELECT 1` probe and returns HTTP `200 OK` JSON (`{"status": "ok", "database": "ok"}`).
  - Install `curl` in the production Dockerfile runtime stage and configure both `HEALTHCHECK` in `compose/production/django/Dockerfile` and `healthcheck:` in `/docker-compose.yaml` (`curl --fail --silent http://127.0.0.1:5000/healthz/`).
- **Configure persistent volumes, first-boot auto-seeding, and automated online SQLite + media backups**:
  - Define Coolify-managed named volumes (`sqlite-data:/app/data`, `media-data:/app/web_result/media`, `backups-data:/app/backups`) in `/docker-compose.yaml` so Coolify tracks them under **Persistent Storage** and **Backups > Storage backups**.
  - Add a `python manage.py backup_data` management command that uses Python's atomic online `sqlite3.Connection.backup()` API (safe during active WAL-mode traffic) and bundles the database snapshot + media files into timestamped `.tar.gz` archives in `/app/backups` (and `/app/data/backups`) with automatic retention pruning (`DJANGO_BACKUP_RETENTION_COUNT`, default `7`) and `--restore <archive>` support.
  - Update `/start` (`compose/production/django/start`) to:
    1. Automatically create a pre-migration backup when an existing SQLite database is present (`DJANGO_AUTO_BACKUP_ON_START=True`).
    2. Automatically import legacy SQL records, student images, and the demo/admin user on first boot when the database has no student records (`DJANGO_AUTO_IMPORT_LEGACY=True`).
    3. Run an optional background periodic backup loop (`DJANGO_AUTO_BACKUP_INTERVAL=86400`).

## Capabilities

### New Capabilities
- `coolify-one-click-deployment`: Coolify-native `/docker-compose.yaml` auto-detection, magic environment variable integration (`SERVICE_FQDN_DJANGO_5000`, `SERVICE_BASE64_64_DJANGO`, `COOLIFY_FQDN`, `COOLIFY_URL`), `/healthz/` container health check, first-boot legacy auto-seeding, and WAL-safe automated SQLite + media backup/restore (`backup_data`).

### Modified Capabilities
- `cookiecutter-sqlite-docker`: Production Docker Compose stack is streamlined to a single `django` service (removing redundant `traefik` and `nginx` containers) and exposed via `/docker-compose.yaml` and `/docker-compose.production.yml` with persistent volumes for SQLite data, media, and backups.

## Impact

- `/docker-compose.yaml` (new) and `/docker-compose.production.yml` (updated)
- `/.env.example` (new)
- `compose/production/django/Dockerfile`, `compose/production/django/entrypoint`, and `compose/production/django/start`
- `config/settings/production.py` and `config/urls.py`
- `web_result/results/views.py` (`HealthCheckView`)
- `web_result/results/management/commands/backup_data.py` (new)
- `web_result/results/tests/test_results.py` (expanded test coverage for healthcheck, Coolify env parsing, and backup/restore)
