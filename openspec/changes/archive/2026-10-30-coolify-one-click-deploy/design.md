## Context

See `proposal.md` for motivation and scope. Coolify deploys Git repositories using its `RepositoryDetector` and `applicationParser` (`bootstrap/helpers/parsers.php`). When `/docker-compose.yaml` is present at the repository root, Coolify automatically selects the `dockercompose` build pack and parses service definitions, magic `SERVICE_*` variables, named volumes, and container health checks.

## Goals / Non-Goals

**Goals:**
- True one-click deployment on Coolify with zero manual UI customization required after connecting the repository.
- Eliminate unnecessary `traefik` and `nginx` containers from the production Compose stack since Coolify runs its own host Traefik reverse proxy and Django serves static files (via WhiteNoise) and media files (`/uploads/` and `/media/` via `DJANGO_SERVE_MEDIA=True`).
- Automatically configure domain routing to internal port `5000`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS` using Coolify magic variables (`SERVICE_FQDN_DJANGO_5000`, `SERVICE_BASE64_64_DJANGO`, `COOLIFY_FQDN`, `COOLIFY_URL`).
- Provide a Coolify-compatible `/healthz/` endpoint and Docker `HEALTHCHECK` that work reliably regardless of `SECURE_SSL_REDIRECT`.
- Automatically seed legacy SQL data and student photos on first boot when the SQLite database is empty, and maintain automated WAL-safe SQLite + media backups in a Coolify-tracked persistent volume (`/app/backups`).

**Non-Goals:**
- Changing the local development stack (`docker-compose.local.yml`).
- Requiring an external PostgreSQL or Redis service.

## Decisions

### 1. Root `/docker-compose.yaml` without `traefik`, `nginx`, or hardcoded `image:`
- **Decision**: Create `/docker-compose.yaml` (and mirror it in `/docker-compose.production.yml`) with only the `django` service (`expose: ["5000"]`, `restart: unless-stopped`) and no `image:` attribute.
- **Rationale**:
  - Coolify's default `docker_compose_location` is `/docker-compose.yaml`, and `RepositoryDetector` prioritizes `/^docker-compose\.ya?ml$/i` in the root directory to auto-select the `dockercompose` build pack.
  - Coolify's `applicationParser` (`bootstrap/helpers/parsers.php`) only injects commit-based image tags (`{uuid}_django:{commit}`) for rollback support when `build:` is present and `image:` is omitted.
  - Omitting host `ports:` prevents port binding conflicts on the Coolify host while `SERVICE_FQDN_DJANGO_5000` instructs Coolify's Traefik proxy to route traffic to container port `5000`.

### 2. Coolify Magic Environment Variables & Dynamic `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS`
- **Decision**:
  - In `/docker-compose.yaml`, declare:
    - `SERVICE_FQDN_DJANGO_5000`
    - `DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:-${SERVICE_BASE64_64_DJANGO}}`
    - `DJANGO_ADMIN_PASSWORD: ${DJANGO_ADMIN_PASSWORD:-${SERVICE_PASSWORD_ADMIN}}`
  - In `config/settings/production.py`, construct `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` dynamically from `DJANGO_ALLOWED_HOSTS`, `COOLIFY_FQDN`, `SERVICE_FQDN_DJANGO`, `SERVICE_FQDN_DJANGO_5000`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `COOLIFY_URL`, `SERVICE_URL_DJANGO`, and `SERVICE_URL_DJANGO_5000`.
- **Rationale**:
  - Coolify's magic variable parser requires single-token `<ID>` suffixes (`DJANGO`, `ADMIN`) and automatically creates both `SERVICE_FQDN_DJANGO` (hostname) and `SERVICE_FQDN_DJANGO_5000` (`hostname:5000`), as well as `COOLIFY_FQDN` and `COOLIFY_URL`.
  - Stripping schemes and `:port` suffixes in Python ensures `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` always match any wildcard or custom domains configured in Coolify without manual env var edits.
  - Defaulting `DJANGO_SECURE_SSL_REDIRECT` to `False` (since Coolify's Traefik handles HTTPS redirects) and dynamically setting `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` based on whether the active URL uses `https://` allows one-click deployments to work immediately on both `http://*.sslip.io` wildcard domains and `https://` custom domains.

### 3. `/healthz/` Endpoint Exempt from SSL Redirect
- **Decision**: Add `HealthCheckView` at `/healthz/` that executes `SELECT 1` on the default database connection and returns `200 OK` (`{"status": "ok", "database": "ok"}`), and set `SECURE_REDIRECT_EXEMPT = [r"^healthz/?$"]` in `config/settings/production.py`. Install `curl` in the runtime image (`compose/production/django/Dockerfile`) and configure `curl --fail --silent http://127.0.0.1:5000/healthz/` in both `Dockerfile` `HEALTHCHECK` and `/docker-compose.yaml` `healthcheck`.
- **Rationale**: Coolify relies on the container's Docker health status to mark deployments healthy and switch Traefik routing. Exempting `/healthz/` from SSL redirect ensures internal plain-HTTP probes never receive a `301` redirect to `https://127.0.0.1:5000`.

### 4. Coolify-Managed Volumes, First-Boot Seeding, and WAL-Safe Online Backups
- **Decision**:
  - Mount three named volumes on `django`:
    - `sqlite-data:/app/data`
    - `media-data:/app/web_result/media`
    - `backups-data:/app/backups`
  - Create `python manage.py backup_data` using `sqlite3.Connection.backup()` to snapshot the live WAL database into a temporary file and bundle it with `MEDIA_ROOT` into `/app/backups/backup-<timestamp>.tar.gz`, keeping the newest `DJANGO_BACKUP_RETENTION_COUNT` (default `7`) archives. Also mirror the latest archive in `/app/data/backups/latest.tar.gz` so Coolify's volume backup of `sqlite-data` always contains an atomic, WAL-checkpointed snapshot.
  - Update `/start` to:
    1. Run a pre-migration backup (`python /app/manage.py backup_data`) if `/app/data/db.sqlite3` already exists.
    2. Run `migrate --noinput` and `collectstatic --noinput`.
    3. If `Student.objects.count() == 0` and `DJANGO_AUTO_IMPORT_LEGACY=True`, automatically run `import_legacy_data` with `/app/old/database/Result.sql`, `/app/old/public/uploads/images`, and `--seed-demo-user`.
    4. Start a background periodic backup loop if `DJANGO_AUTO_BACKUP_INTERVAL > 0`.
- **Rationale**: Coolify's docs explicitly warn that file-level `.tar.gz` volume backups of live databases can capture inconsistent state if files change mid-archive. Using `sqlite3.Connection.backup()` produces a 100% transactionally consistent SQLite snapshot while Gunicorn serves requests.

## Risks / Trade-offs

- **[Risk] Coolify wildcard domain initially uses `http://` before Let's Encrypt is enabled** → **Mitigation**: `config/settings/production.py` inspects `SERVICE_URL_DJANGO` / `COOLIFY_URL` to disable `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` automatically when the URL starts with `http://`, and defaults `SECURE_SSL_REDIRECT` to `False` so Traefik manages HTTPS redirection.
- **[Risk] First-boot auto-seed re-running on subsequent restarts** → **Mitigation**: `/start` checks whether any `Student` or `Semester` records already exist in SQLite before running `import_legacy_data`, and `import_legacy_data` itself uses idempotent `update_or_create`.
