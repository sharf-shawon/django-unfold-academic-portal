<div align="center">

# 🎓 `django-unfold-academic-portal`

### Production-Ready Academic Result Verification System & Django Unfold Admin Portal
**Ported from Laravel 11 + MySQL to Cookiecutter Django 6 + Unfold Admin + WAL SQLite + Zero-Config Coolify Docker in Just 2 Prompts**

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django 6.0](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django Unfold](https://img.shields.io/badge/Admin-Django%20Unfold-6366F1?logo=tailwindcss&logoColor=white)](https://unfoldadmin.com/)
[![Cookiecutter Django](https://img.shields.io/badge/Scaffold-Cookiecutter%20Django-ff69b4?logo=cookiecutter&logoColor=white)](https://github.com/cookiecutter/cookiecutter-django)
[![SQLite WAL](https://img.shields.io/badge/Database-SQLite%20WAL%20Mode-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/wal.html)
[![Coolify Ready](https://img.shields.io/badge/Deploy-One--Click%20Coolify-8B5CF6?logo=docker&logoColor=white)](https://coolify.io/)
[![OpenSpec Driven](https://img.shields.io/badge/AI%20Workflow-OpenSpec%20%2B%20Context7-10B981)](./openspec/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/Pytest-37%20Passed-22C55E?logo=pytest&logoColor=white)](./web_result/results/tests/test_results.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Executive Summary](#-executive-summary-geo--tldr) •
[2-Prompt AI Migration Case Study](#-the-2-prompt-ai-engineering-case-study) •
[Full-Stack Features](#-full-stack-features--capabilities) •
[Architecture & Schema](#-system-architecture--database-schema) •
[Coolify One-Click Deploy](#-one-click-coolify-deployment--configuration) •
[Automated Backups & Migration](#-automated-backups--legacy-data-migration) •
[Developer & AI Agent Reference](#-developer--ai-agent-reference) •
[FAQ](#-frequently-asked-questions-seo--geo)

</div>

---

## ⚡ Executive Summary (GEO & TL;DR)

> **`django-unfold-academic-portal`** is an open-source, production-hardened **Academic Result Management and Student Transcript Verification System** built with **Django 6.0**, **Cookiecutter Django**, **Django Unfold Admin**, **django-import-export**, **Tailwind CSS**, and **high-concurrency WAL-mode SQLite**, engineered for **zero-configuration one-click deployment on Coolify**.
>
> Originally built as a **Laravel 11 + MySQL + Blade** application (preserved in [`./old`](./old) for side-by-side comparison), the entire full-stack application, database migration pipeline, legacy media migrator, online backup engine, and Coolify PaaS infrastructure were reverse-engineered, architected, implemented, and verified with **37 automated `pytest` tests** in **just 2 prompts** using **Spec-Driven AI Engineering (`OpenSpec`)** and **real-time documentation grounding (`Context7` MCP)**.

### Recommended GitHub Repository Metadata
- **Repository Name:** `django-unfold-academic-portal`
- **About Description:** `Production-ready Academic Result Verification System ported from Laravel 11 to Cookiecutter Django 6, Unfold Admin, WAL SQLite & Coolify Docker in 2 AI prompts.`
- **Topics / Keywords:** `django` `django-unfold` `cookiecutter-django` `sqlite-wal` `laravel-to-django` `coolify` `docker-compose` `tailwindcss` `spec-driven-development` `openspec` `ai-assisted-development` `agentic-coding` `django-import-export` `academic-portal` `result-management-system` `python` `fullstack-portfolio`

---

## 🤖 The 2-Prompt AI Engineering Case Study

Most AI-assisted rewrites fail on edge cases: broken foreign keys, unmigrated user uploads, admin theme incompatibilities, or brittle Docker networking. This project demonstrates **AI-Native Senior Full-Stack Engineering**—combining **formal specifications (`OpenSpec`)**, **live documentation retrieval (`Context7`)**, and **deterministic verification (`pytest` + `ruff`)** to execute a complete cross-framework migration in **2 prompts**:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│           The 2-Prompt Spec-Driven AI Migration Workflow                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PROMPT 1: Legacy Reverse-Engineering & Full-Stack Application Port          │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Analyzed legacy Laravel 11 models, controllers, & MySQL dump (./old)│  │
│  │ 2. Scaffolded Cookiecutter Django 6 with WAL-mode SQLite persistence   │  │
│  │ 3. Ported Semester, Course, Student, StudentCourse, & Result models    │  │
│  │ 4. Configured Django Unfold Admin + django-import-export across all    │  │
│  │    academic AND built-in Cookiecutter Django (Auth/Allauth/Sites) apps │  │
│  │ 5. Built dual-engine MySQL .sql dump + student photo migration CLI     │  │
│  │ 6. Replicated pixel-accurate Tailwind CSS Student Verification Portal  │  │
│  └──────────────────────────────────┬─────────────────────────────────────┘  │
│                                     ▼                                        │
│  PROMPT 2: Zero-Config Coolify PaaS & Production Hardening                   │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Grounded against official Coolify docs & parser source via Context7 │  │
│  │ 2. Created root /docker-compose.yaml (removed redundant Nginx/Traefik) │  │
│  │ 3. Wired Coolify magic variables (SERVICE_FQDN_DJANGO_5000,            │  │
│  │    SERVICE_BASE64_64_DJANGO, COOLIFY_FQDN, COOLIFY_URL)                │  │
│  │ 4. Added SSL-redirect-exempt /healthz/ SQLite probe & Docker healthcheck│ │
│  │ 5. Built first-boot legacy auto-seeder & online WAL-safe SQLite +      │  │
│  │    media backup/restore engine (python manage.py backup_data)          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Why Only 2 Prompts Were Needed
1. **Spec-Driven Planning Before Code (`OpenSpec`)**: Every architectural decision, requirement, and scenario was captured in [`openspec/specs/`](./openspec/specs/) and [`openspec/changes/archive/`](./openspec/changes/archive/) before writing application code.
2. **Zero-Hallucination Documentation Grounding (`Context7`)**: Live documentation for `Cookiecutter Django`, `django-unfold`, `django-import-export`, and `Coolify` was queried directly during planning.
3. **Closed-Loop Self-Verification**: Every task was validated against `uv run ruff check`, `uv run python manage.py check`, `uv run pytest`, and `openspec validate --all --strict`.

---

## 🚀 Full-Stack Features & Capabilities

### 1. Public Student Transcript & Result Verification Portal (`GET /`, `POST /`)
- **Instant Academic Verification**: Students and employers verify academic transcripts by entering a **Student ID** and **Date of Birth** on the public index page ([`web_result/results/views.py`](./web_result/results/views.py)).
- **1-to-1 Legacy Visual Parity**: Replicates the exact responsive Tailwind CSS layout, student photo header, metadata grid (Name, Student ID, Department, Session, Date of Birth, CGPA, Date of Issue), and semester-by-semester course GPA table ([`web_result/templates/results/show.html`](./web_result/templates/results/show.html)).
- **Optimized ORM Queries**: Uses `select_related("course", "course__semester")` and `Prefetch` to render full student transcripts with zero N+1 queries.

### 2. Unified Django Unfold Admin & Browser Import/Export (`/admin/`)
- **Modern Tailwind Admin UI**: Powered by [`django-unfold`](https://unfoldadmin.com/) with custom sidebar navigation, search, filters, and inline course enrollment editing ([`web_result/results/admin.py`](./web_result/results/admin.py)).
- **Complete Model Coverage**: Every registered model—both new academic models (`Student`, `Semester`, `Course`, `Result`) and all Cookiecutter Django default models (`User`, `Group`, `Site`, `EmailAddress`, `SocialAccount`, `SocialToken`, `SocialApp`)—inherits from `unfold.admin.ModelAdmin` ([`web_result/users/admin.py`](./web_result/users/admin.py)) and is verified by automated tests.
- **Browser CSV / XLSX / JSON Import & Export**: Integrated with `django-import-export` and `unfold.contrib.import_export` so administrators can bulk-import or export academic records directly from the browser.
- **Locked-Down Authentication**: Public sign-up is disabled by default (`ACCOUNT_ALLOW_REGISTRATION = False`), restricting portal administration to authorized staff accounts.

### 3. Production-Grade High-Concurrency SQLite (WAL Mode)
Instead of requiring a heavyweight PostgreSQL container for a read-heavy academic portal, [`config/settings/base.py`](./config/settings/base.py) configures SQLite for concurrent production workloads:
- `PRAGMA journal_mode=WAL;` (concurrent readers alongside writers)
- `PRAGMA synchronous=NORMAL;`
- `PRAGMA busy_timeout=20000;` (20-second lock wait timeout)
- `PRAGMA foreign_keys=ON;`
- `transaction_mode="IMMEDIATE"`

### 4. Dual-Engine Legacy MySQL & Media Migration
- **CLI Migration Command (`import_legacy_data`)**: Parses legacy MySQL `.sql` dumps ([`./old/database/Result.sql`](./old/database/Result.sql)) or connects directly to a live MySQL instance (`--mysql-url`), preserving primary keys, foreign keys, and timestamps while migrating student photos into `MEDIA_ROOT/images/` and seeding the admin user ([`web_result/results/management/commands/import_legacy_data.py`](./web_result/results/management/commands/import_legacy_data.py)).
- **First-Boot Zero-Touch Seeding**: On initial container startup, if `Student.objects.count() == 0` and `DJANGO_AUTO_IMPORT_LEGACY=True`, [`compose/production/django/start`](./compose/production/django/start) automatically imports [`./old/database/Result.sql`](./old/database/Result.sql), copies [`./old/public/uploads`](./old/public/uploads), and seeds the demo admin user (`demo@shawon.me` / `demo1234`).

### 5. Online WAL-Safe SQLite + Media Automated Backups
- **Atomic Online Backups (`backup_data`)**: Uses Python's native `sqlite3.Connection.backup()` API to capture a transactionally consistent snapshot of the live WAL database without locking or stopping Gunicorn, bundling `db.sqlite3` and `MEDIA_ROOT` into timestamped `.tar.gz` archives ([`web_result/results/management/commands/backup_data.py`](./web_result/results/management/commands/backup_data.py)).
- **3-Layer Backup Protection**:
  1. **Pre-Deployment Backup**: Runs automatically in `/start` before `manage.py migrate` whenever an existing database is detected.
  2. **Periodic In-Container Backup Daemon**: Runs every `DJANGO_AUTO_BACKUP_INTERVAL` seconds (default `86400` / 24 hours) and prunes archives beyond `DJANGO_BACKUP_RETENTION_COUNT` (default `7`).
  3. **Coolify Volume Backup Sync**: Mirrors the latest consistent archive to `/app/data/backups/latest.tar.gz` and `/app/backups/` so Coolify's scheduled local/S3 **Storage Backups** always capture an atomic SQLite snapshot.

---

## 🏗️ System Architecture & Database Schema

### Legacy Laravel 11 vs. Modernized Django 6 Architecture

| Layer | Legacy Stack (`./old`) | Modernized Stack (`/`) | Engineering Upgrade |
| :--- | :--- | :--- | :--- |
| **Framework** | Laravel 11 (PHP 8.2) | Cookiecutter Django 6.0 (Python 3.13) | Strict type checks (`mypy`), `ruff`, `uv` lockfile |
| **Database** | MySQL 8.0 | SQLite 3 (`journal_mode=WAL`) | Zero external DB container overhead; persistent Docker volume |
| **Admin CRUD** | Custom Blade CRUD views (with incomplete `CourseController::destroy`) | **Django Unfold Admin** + `django-import-export` | Full CRUD (including working Course deletion), search, filters, inline M2M, CSV/JSON/XLSX import/export |
| **Public Portal** | `ResultPublicController` + Tailwind CSS | `ResultPublicView` (`GET /`, `POST /`) + Tailwind CSS | Identical UI/UX with `Prefetch` query optimization |
| **Static & Media** | PHP Artisan / Apache + `public/uploads/` | `WhiteNoise` (`/static/`) + Django `/uploads/` & `/media/` | Single-container serving behind Coolify's Traefik proxy |
| **Deployment** | Manual PHP/MySQL hosting | Root [`/docker-compose.yaml`](./docker-compose.yaml) for **Coolify** | 1-click deploy, magic env vars, `/healthz/` probe, commit-tagged rollbacks |

### Entity-Relationship Diagram (`web_result.results`)

```mermaid
erDiagram
    SEMESTER ||--o{ COURSE : "has many (CASCADE)"
    STUDENT ||--o{ RESULT : "has many (CASCADE)"
    COURSE ||--o{ RESULT : "has many (CASCADE)"
    STUDENT ||--o{ STUDENT_COURSE : "enrolled in (CASCADE)"
    COURSE ||--o{ STUDENT_COURSE : "enrolls (CASCADE)"

    SEMESTER {
        bigint id PK
        varchar name
        varchar year
        datetime created_at
        datetime updated_at
    }
    COURSE {
        bigint id PK
        varchar name
        varchar code
        bigint semester_id FK
        datetime created_at
        datetime updated_at
    }
    STUDENT {
        bigint id PK
        varchar student_id "Indexed lookup key"
        varchar name
        varchar email "Unique"
        varchar phone
        varchar address
        varchar session
        varchar department
        date date_of_birth "Verification key"
        date date_of_issue
        decimal cgpa "max_digits=3, decimal_places=2"
        varchar image "Uploads to images/"
        datetime created_at
        datetime updated_at
    }
    STUDENT_COURSE {
        bigint id PK
        bigint course_id FK
        bigint student_id FK
    }
    RESULT {
        bigint id PK
        bigint course_id FK
        bigint student_id FK
        decimal gpa "max_digits=3, decimal_places=2"
        datetime created_at
        datetime updated_at
    }
```

### Coolify Production Container Architecture

```mermaid
flowchart LR
    User(["Student / Admin Browser"])
    Traefik["Coolify Host Traefik Proxy\n(Auto TLS + Domain Routing)"]
    subgraph Container["Single Production Container: django (Port 5000)"]
        Gunicorn["Gunicorn WSGI\n0.0.0.0:5000"]
        WhiteNoise["WhiteNoise\n/static/"]
        MediaServe["Django Media View\n/uploads/ & /media/"]
        Healthz["HealthCheckView\nGET /healthz/"]
        BackupDaemon["Online Backup Daemon\nmanage.py backup_data"]
    end
    subgraph Volumes["Coolify Managed Persistent Volumes"]
        SQLiteVol[("sqlite-data\n/app/data/db.sqlite3")]
        MediaVol[("media-data\n/app/web_result/media")]
        BackupVol[("backups-data\n/app/backups/*.tar.gz")]
    end

    User -- "HTTPS (80/443)" --> Traefik
    Traefik -- "SERVICE_FQDN_DJANGO_5000\nhttp://django:5000" --> Gunicorn
    Gunicorn --> WhiteNoise
    Gunicorn --> MediaServe
    Gunicorn --> Healthz
    Gunicorn <--> SQLiteVol
    MediaServe <--> MediaVol
    BackupDaemon -- "sqlite3.backup()" --> SQLiteVol
    BackupDaemon -- "tar.gz" --> BackupVol
```

---

## ☁️ One-Click Coolify Deployment & Configuration

This repository is engineered to deploy on [**Coolify**](https://coolify.io/) with **zero manual configuration**:

### Step-by-Step One-Click Deployment
1. In your Coolify dashboard, click **+ New** → **Application** → select your Git source and pick this repository.
2. **Auto-Detection**:
   - Coolify's Smart Scan (`RepositoryDetector`) automatically finds [`/docker-compose.yaml`](./docker-compose.yaml) at the repository root and selects the **Docker Compose** build pack.
   - Coolify also detects [`/.env.example`](./.env.example) at the root.
3. Click **Deploy**. No environment variables, ports, domains, or volumes need to be manually configured!

### How Zero-Config Coolify Integration Works Under the Hood
- **No Redundant Proxy Containers**: Coolify already runs Traefik on the host. [`/docker-compose.yaml`](./docker-compose.yaml) runs only the `django` service (`expose: ["5000"]`), removing unnecessary `nginx` and `traefik` sidecars.
- **Commit-Tagged Rollbacks**: [`/docker-compose.yaml`](./docker-compose.yaml) intentionally omits a hardcoded `image:` name on the `django` service so Coolify's parser automatically tags built images as `{uuid}_django:{commit_sha}`, enabling one-click rollbacks in Coolify.
- **Coolify Magic Environment Variables**:
  - `SERVICE_FQDN_DJANGO_5000`: Instructs Coolify to auto-generate/assign the application domain to the `django` service and route Traefik to internal container port `5000`.
  - `SERVICE_BASE64_64_DJANGO`: Instructs Coolify to generate and persist a cryptographically random 64-character `DJANGO_SECRET_KEY`.
  - `SERVICE_PASSWORD_ADMIN`: Generates a persistent random password token in Coolify's Environment Variables tab.
- **Dynamic Host, CSRF & Cookie Resolution ([`config/settings/production.py`](./config/settings/production.py))**:
  - [`build_coolify_hosts_and_origins()`](./config/settings/production.py) automatically reads `DJANGO_ALLOWED_HOSTS`, `COOLIFY_FQDN`, `SERVICE_FQDN_DJANGO`, `SERVICE_FQDN_DJANGO_5000`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `COOLIFY_URL`, `SERVICE_URL_DJANGO`, and `SERVICE_URL_DJANGO_5000`.
  - Strips `:5000` port suffixes from hostnames/origins and automatically adapts `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` so the app works immediately on both `http://*.sslip.io` temporary wildcard domains and `https://` custom production domains.
- **SSL-Exempt Container Health Check (`/healthz/`)**:
  - Both [`compose/production/django/Dockerfile`](./compose/production/django/Dockerfile) and [`/docker-compose.yaml`](./docker-compose.yaml) run `curl --fail --silent http://127.0.0.1:5000/healthz/`.
  - `SECURE_REDIRECT_EXEMPT = [r"^healthz/?$"]` ensures `/healthz/` always returns `200 OK` (`{"status": "ok", "database": "ok"}`) over internal plain HTTP even if `DJANGO_SECURE_SSL_REDIRECT=True`.

---

## 💾 Automated Backups & Legacy Data Migration

### 1. Online SQLite + Media Backup & Restore (`backup_data`)

Create an immediate WAL-safe online backup archive (database + uploaded student photos):

```bash
# Inside local environment (uv)
uv run python manage.py backup_data

# Inside running production container
docker compose -f docker-compose.yaml exec django python manage.py backup_data --keep 7
```

Restore the SQLite database and media files from any `.tar.gz` backup archive:

```bash
uv run python manage.py backup_data --restore /app/backups/web-result-backup-YYYYMMDD-HHMMSS.tar.gz
```

**Where Backups Are Stored in Production:**
- `/app/backups/web-result-backup-<timestamp>.tar.gz` (mounted to the `backups-data` persistent Docker volume).
- `/app/data/backups/latest.tar.gz` (mirrored inside the `sqlite-data` volume so Coolify's **Backups → Storage backups** UI captures an atomic SQLite snapshot even during live traffic).

### 2. Legacy MySQL & Student Photo Migration (`import_legacy_data`)

Import academic records from a legacy MySQL `.sql` dump or live MySQL connection and copy student photos into `MEDIA_ROOT/images/`:

```bash
# Import from the historic Laravel SQL dump + migrate student photos + seed demo admin
uv run python manage.py import_legacy_data \
  --sql-file ./old/database/Result.sql \
  --uploads-dir ./old/public/uploads \
  --seed-demo-user

# Or import directly from a live MySQL database URL
uv run python manage.py import_legacy_data \
  --mysql-url "mysql://user:pass@host:3306/result" \
  --uploads-dir ./old/public/uploads
```

> **Note:** Legacy `users` table rows from Laravel are intentionally skipped; authentication uses Cookiecutter Django's email-based `User` model (`demo@shawon.me` / `demo1234` by default).

---

## 🛠️ Developer & AI Agent Reference

### Repository Directory Structure

```text
.
├── compose/
│   ├── local/django/               # Local development Dockerfile, entrypoint & start scripts
│   └── production/django/          # Coolify/Production multi-stage uv Dockerfile, entrypoint & start
├── config/
│   ├── settings/
│   │   ├── base.py                 # WAL SQLite, Unfold Admin, Allauth, WhiteNoise & Media settings
│   │   ├── local.py                # Local debug & Mailpit settings
│   │   ├── production.py           # Coolify magic env parser, security headers & logging
│   │   └── test.py                 # Fast password hasher & test settings
│   └── urls.py                     # Root URL routing (/, /healthz/, /admin/, /uploads/, /accounts/)
├── old/                            # Historic Laravel 11 + MySQL project & Result.sql dump (read-only reference)
├── openspec/
│   ├── specs/                      # 5 canonical system specifications (source of truth for AI agents)
│   └── changes/archive/            # Archived proposals, designs, delta specs & task checklists
├── web_result/
│   ├── results/
│   │   ├── management/commands/
│   │   │   ├── backup_data.py      # Online SQLite .backup() + media tar.gz archiver & restorer
│   │   │   └── import_legacy_data.py # Legacy MySQL .sql / live DB + photo migrator
│   │   ├── migrations/             # Django schema migrations
│   │   ├── tests/test_results.py   # Comprehensive pytest suite (Unfold, Public Portal, CLI, Coolify)
│   │   ├── admin.py                # Unfold ModelAdmin + django-import-export resources
│   │   ├── forms.py                # ResultSearchForm (student_id + date_of_birth validation)
│   │   ├── models.py               # Semester, Course, Student, StudentCourse, Result
│   │   └── views.py                # ResultPublicView (GET/POST /) & HealthCheckView (GET /healthz/)
│   ├── templates/results/          # Tailwind CSS templates (base_guest.html, index.html, show.html)
│   └── users/                      # Email-based custom User model & Unfold Admin registrations
├── .env.example                    # Auto-detected by Coolify Smart Scan
├── docker-compose.yaml             # Primary Coolify zero-config production Compose definition
├── docker-compose.production.yml   # Production Compose definition (synced with docker-compose.yaml)
├── docker-compose.local.yml        # Local development Compose stack (Django + Mailpit)
└── pyproject.toml                  # Python 3.13 dependencies managed by Astral uv
```

### Environment Variables Matrix

| Variable | Default in `docker-compose.yaml` | Purpose |
| :--- | :--- | :--- |
| `SERVICE_FQDN_DJANGO_5000` | *(Coolify Magic Variable)* | Auto-assigns Coolify domain & routes Traefik proxy to container port `5000` |
| `DJANGO_SECRET_KEY` | `${SERVICE_BASE64_64_DJANGO}` | Uses Coolify's 64-character random generator (with safe fallback) |
| `DJANGO_ALLOWED_HOSTS` | Auto-resolved | Merged with `COOLIFY_FQDN`, `SERVICE_FQDN_DJANGO`, `localhost`, `127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Auto-resolved | Merged with `COOLIFY_URL`, `SERVICE_URL_DJANGO`, and `https://<host>` |
| `DJANGO_ADMIN_URL` | `admin/` | Path to the Django Unfold Admin portal |
| `DJANGO_ADMIN_EMAIL` | `demo@shawon.me` | Admin email seeded on first boot when `DJANGO_AUTO_IMPORT_LEGACY=True` |
| `DJANGO_ADMIN_PASSWORD` | `demo1234` | Admin password seeded on first boot |
| `DJANGO_SECURE_SSL_REDIRECT` | `False` | `False` by default because Coolify's Traefik proxy handles HTTPS redirection |
| `DJANGO_SERVE_MEDIA` | `True` | Serves `/uploads/` and `/media/` directly from the `django` container |
| `DJANGO_AUTO_IMPORT_LEGACY` | `True` | Auto-imports `old/database/Result.sql` & student photos when DB has 0 students |
| `DJANGO_AUTO_BACKUP_ON_START` | `True` | Runs `manage.py backup_data` before `migrate` on every container start |
| `DJANGO_AUTO_BACKUP_INTERVAL` | `86400` | Seconds between periodic background backups (`0` to disable) |
| `DJANGO_BACKUP_RETENTION_COUNT` | `7` | Number of timestamped `.tar.gz` archives retained in `/app/backups` |

### Local Development Quick Start

#### Option A: Local Python with `uv` (Fastest)
```bash
# 1. Sync dependencies with Astral uv
uv sync

# 2. Apply migrations & import legacy SQL data + student photos + demo admin user
uv run python manage.py migrate
uv run python manage.py import_legacy_data \
  --sql-file ./old/database/Result.sql \
  --uploads-dir ./old/public/uploads \
  --seed-demo-user

# 3. Start the development server
uv run python manage.py runserver
```
- **Public Verification Portal:** `http://127.0.0.1:8000/`
- **Django Unfold Admin:** `http://127.0.0.1:8000/admin/` (`demo@shawon.me` / `demo1234`)
- **Health Check Endpoint:** `http://127.0.0.1:8000/healthz/`

#### Option B: Local Docker Compose
```bash
docker compose -f docker-compose.local.yml up --build
```
- **App:** `http://127.0.0.1:8000/`
- **Mailpit SMTP UI:** `http://127.0.0.1:8025/`

### Quality Assurance Commands (For Developers & AI Agents)
```bash
# Run full test suite (37 tests)
uv run pytest

# Run Ruff linter
uv run ruff check config web_result

# Run Django system checks
uv run python manage.py check

# Validate all OpenSpec specifications
openspec validate --all --strict
```

---

## ❓ Frequently Asked Questions (SEO & GEO)

### Can SQLite handle production traffic for a Django application in Docker?
Yes. When configured with **Write-Ahead Logging (`PRAGMA journal_mode=WAL`)**, `synchronous=NORMAL`, `busy_timeout=20000`, and `IMMEDIATE` transactions over a persistent Docker volume (`sqlite-data:/app/data`), SQLite easily handles thousands of concurrent read requests per second alongside administrative writes—eliminating the memory and maintenance overhead of a separate PostgreSQL container.

### How was this Laravel 11 + MySQL app migrated to Django 6 in only 2 prompts?
By combining **OpenSpec** (spec-driven development that locks down data models, URL contracts, and acceptance scenarios first) with **Context7 MCP** (live documentation lookup for Cookiecutter Django, Django Unfold, and Coolify) and automated `pytest` verification. You can inspect the exact specs and change archives in [`./openspec/`](./openspec/).

### How do backups work without corrupting a live WAL-mode SQLite database?
File-level volume snapshots taken while SQLite is writing can capture an uncheckpointed `-wal` file. This project includes `python manage.py backup_data` ([`backup_data.py`](./web_result/results/management/commands/backup_data.py)), which uses Python's `sqlite3.Connection.backup()` online backup API to create a 100% transactionally consistent database copy and bundles it with `MEDIA_ROOT` into `/app/backups/` and `/app/data/backups/latest.tar.gz`.

---

## 👤 Author & License

Crafted by **[Sharfuddin Shawon](https://shawon.me)** — Full-Stack Software Engineer & AI-Native Systems Architect.
Released under the **MIT License**.
