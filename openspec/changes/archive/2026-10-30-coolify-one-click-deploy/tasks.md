## 1. Coolify Docker Compose, Environment Template, and Container Healthcheck

- [x] 1.1 Create `/docker-compose.yaml` and update `/docker-compose.production.yml` with a single `django` service (removing `traefik` and `nginx`), omitting a hardcoded `image:` tag, exposing internal port `5000`, declaring Coolify magic variables (`SERVICE_FQDN_DJANGO_5000`, `SERVICE_BASE64_64_DJANGO`, `SERVICE_PASSWORD_ADMIN`), defining a `curl --fail --silent http://127.0.0.1:5000/healthz/` healthcheck, and mounting named volumes (`sqlite-data:/app/data`, `media-data:/app/web_result/media`, `backups-data:/app/backups`)
- [x] 1.2 Create `/.env.example` at the repository root so Coolify's Smart Scan (`RepositoryDetector`) detects all supported environment variables and defaults
- [x] 1.3 Update `compose/production/django/Dockerfile` and `compose/production/django/entrypoint` to install `curl`, initialize `/app/backups` alongside `/app/data` and `/app/web_result/media`, expose port `5000`, and declare a Dockerfile `HEALTHCHECK` against `http://127.0.0.1:5000/healthz/`

## 2. Dynamic Coolify Settings and Healthcheck Endpoint

- [x] 2.1 Update `config/settings/production.py` to dynamically resolve ` SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SECURE_SSL_REDIRECT`, `SECURE_REDIRECT_EXEMPT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE` from Coolify magic and predefined environment variables (`SERVICE_BASE64_64_DJANGO`, `COOLIFY_FQDN`, `COOLIFY_URL`, `SERVICE_FQDN_DJANGO`, `SERVICE_FQDN_DJANGO_5000`, `SERVICE_URL_DJANGO`, `SERVICE_URL_DJANGO_5000`)
- [x] 2.2 Implement `HealthCheckView` (`GET /healthz/`) in `web_result/results/views.py` and register `path("healthz/", ...)` in `config/urls.py` to execute a SQLite `SELECT 1` probe and return HTTP `200 OK` JSON

## 3. Automated WAL-Safe Backups and First-Boot Legacy Seeding

- [x] 3.1 Implement `web_result/results/management/commands/backup_data.py` using Python's online `sqlite3.Connection.backup()` API to create timestamped `.tar.gz` archives (SQLite database + uploaded media) in `/app/backups` (and `/app/data/backups/latest.tar.gz`) with retention pruning (`--keep`) and `--restore <archive>` support
- [x] 3.2 Update `compose/production/django/start` to run a pre-migration backup when `/app/data/db.sqlite3` exists (`DJANGO_AUTO_BACKUP_ON_START=True`), automatically import legacy SQL data, student photos, and demo/admin user on first boot when `Student.objects.count() == 0` (`DJANGO_AUTO_IMPORT_LEGACY=True`), and launch a background periodic backup loop (`DJANGO_AUTO_BACKUP_INTERVAL`)

## 4. Verification and Automated Tests

- [x] 4.1 Expand `web_result/results/tests/test_results.py` to test `/healthz/` (including with `SECURE_SSL_REDIRECT=True`), Coolify magic environment variable parsing in `config/settings/production.py`, `backup_data` creation/retention/restore, and `/docker-compose.yaml` structure, then verify with `pytest`, `ruff`, and `openspec validate`
