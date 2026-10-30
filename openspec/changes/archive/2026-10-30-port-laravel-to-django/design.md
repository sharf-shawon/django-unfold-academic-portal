## Context

See `proposal.md` for motivation. The historic Laravel 11 app in `./old` uses MySQL 8, Blade + Tailwind CSS + Alpine.js, and custom CRUD controllers for `Semester`, `Course`, `Student`, and `Result`. The new application replaces the backend and custom CRUD views with a Cookiecutter Django project in the repository root (`/Users/mshawon/Developer/web-result`), backed by SQLite in Docker, `django-unfold` + `django-import-export` for administration, and a faithful port of the public student result verification portal (`/`).

## Goals / Non-Goals

**Goals:**
- Generate a Cookiecutter Django project (`project_slug: web_result`, `username_type: email`, `use_docker: y`, `use_whitenoise: y`) at the repository root alongside `./old`.
- Replace PostgreSQL with a production-ready WAL-mode SQLite configuration (`/app/data/db.sqlite3` in Docker, `data/db.sqlite3` locally).
- Configure `django-unfold` (`unfold`, `unfold.contrib.filters`, `unfold.contrib.forms`, `unfold.contrib.inlines`, `unfold.contrib.import_export`) so all built-in/Cookiecutter models (`User`, `Group`, `Site`, `allauth` `EmailAddress`) and all academic models (`Semester`, `Course`, `Student`, `Result`) are styled and functional in Unfold Admin.
- Replicate the public result verification portal (`GET /` and `POST /`) with the exact same layout, dark/light styling, and student photo rendering.
- Provide seamless migration for both legacy MySQL data (`--sql-file` and `--mysql-url`) and legacy uploaded student photos (`--uploads-dir`, `/uploads/` URL routing).

**Non-Goals:**
- Recreating Laravel's custom frontend CRUD routes (`/student`, `/course`, `/semester`, `/result`)—all record management is handled via Django Unfold Admin (`/admin/`).
- Migrating legacy `users` rows from MySQL (admins use Django's `User` model, with `demo@shawon.me` / `demo1234` seeded via a management command / migration).

## Decisions

### 1. SQLite with WAL Mode & Directory Volume Mounting in Docker
- **Decision**: Configure `DATABASES["default"]` to use `django.db.backends.sqlite3` pointing to `data/db.sqlite3` (overridable via `DATABASE_URL`), with Django 5.1+ `OPTIONS`:
  - `"transaction_mode": "IMMEDIATE"`
  - `"timeout": 20`
  - `"init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA busy_timeout=20000; PRAGMA foreign_keys=ON;"`
  In `docker-compose.local.yml` and `docker-compose.production.yml`, mount a named volume (`sqlite_data:/app/data`) rather than a single file.
- **Rationale**: SQLite WAL mode creates `-wal` and `-shm` sidecar files in the same directory as the database file. Mounting `/app/data` as a directory volume ensures atomic WAL operations and persistence across container restarts while removing the memory and operational overhead of a separate PostgreSQL container.
- **Alternatives Considered**: Mounting `./db.sqlite3:/app/db.sqlite3` directly (rejected because single-file bind mounts in Docker break SQLite WAL file creation and inode locking).

### 2. Exact Legacy Table & Column Naming for Zero-Friction Data Reuse
- **Decision**: Define `Semester`, `Course`, `Student`, and `Result` in `web_result/results/models.py` with explicit `db_table` (`semesters`, `courses`, `students`, `results`) and `db_column` (`semester_id`, `student_id`, `course_id`) matching the Laravel migrations (`2024_03_17_*.php`), plus an explicit `StudentCourse` (`db_table = "course_student"`) through model for `Student.courses`.
- **Rationale**: Note that in `./old`, `students.id` is the integer primary key, `students.student_id` is the unique string roll ID, and `results.student_id` is the foreign key to `students.id`. Mapping `Result.student = models.ForeignKey(Student, db_column="student_id", ...)` preserves exact column compatibility with legacy MySQL dumps and CSV exports.

### 3. Unified `django-unfold` Admin for Built-in and New Models
- **Decision**: Place `"unfold"`, `"unfold.contrib.filters"`, `"unfold.contrib.forms"`, `"unfold.contrib.inlines"`, and `"unfold.contrib.import_export"` before `"django.contrib.admin"` in `INSTALLED_APPS`. Update `web_result/users/admin.py` so `UserAdmin` inherits from `(BaseUserAdmin, unfold.admin.ModelAdmin)` using Unfold's `UserChangeForm`, `UserCreationForm`, and `AdminPasswordChangeForm`, and re-register `Group`, `Site` (`django.contrib.sites`), and `allauth` models (`EmailAddress`) with `unfold.admin.ModelAdmin`. Register `Semester`, `Course`, `Student`, and `Result` with `(unfold.admin.ModelAdmin, ImportExportModelAdmin)` and `ImportForm` / `ExportForm`.
- **Rationale**: By default, third-party and built-in Django admin classes (`Group`, `Site`, `EmailAddress`) inherit from `django.contrib.admin.ModelAdmin` and appear unstyled inside Unfold unless unregistered and re-registered with `unfold.admin.ModelAdmin`.

### 4. Dual Legacy Data & Uploaded Media Migration (`import_legacy_data`)
- **Decision**:
  1. Set `MEDIA_URL = "/uploads/"` (and also serve `/media/` as an alias) with `MEDIA_ROOT = BASE_DIR / "web_result" / "media"`. Because the legacy database stores `image = "images/<filename>"` and the legacy Blade view rendered `url("uploads/{$student->image}")`, setting `MEDIA_URL = "/uploads/"` means both `{{ student.image.url }}` and `/uploads/images/<filename>` resolve identically to `/uploads/images/<filename>`.
  2. Implement `python manage.py import_legacy_data` supporting:
     - `--sql-file <path>`: Tokenizes MySQL `INSERT INTO` statements for `semesters`, `courses`, `students`, `course_student`, and `results`.
     - `--mysql-url <url>`: Connects to a live MySQL database via `pymysql` and reads those tables.
     - `--uploads-dir <path>` (defaulting to `./old/public/uploads` if it exists): Copies uploaded files (`images/*`) into `MEDIA_ROOT/images/` while preserving filenames.
     - `--seed-demo-user`: Creates/updates the `demo@shawon.me` (`demo1234`) staff/superuser account.

## Risks / Trade-offs

- **[Risk] Static & Media File Serving in Production Docker without S3** → **Mitigation**: Cookiecutter Django uses WhiteNoise for static files. For local/persistent media files (`student.image`) in a self-contained SQLite Docker deployment, configure Django/WhiteNoise or ASGI/URL patterns to serve `MEDIA_ROOT` at `/uploads/` (controlled by an environment flag `DJANGO_SERVE_MEDIA=True`, enabled by default in local and standalone Docker deployments) alongside a persistent `django_media` Docker volume.
- **[Risk] Unstyled Third-Party Admin Pages in Unfold** → **Mitigation**: Explicitly audit all registered models in `admin.site._registry` via automated tests to guarantee every registered `ModelAdmin` in the project inherits from `unfold.admin.ModelAdmin`.

## Migration Plan

1. Generate the Cookiecutter Django scaffold at `/Users/mshawon/Developer/web-result` and adapt `config/`, `compose/`, and `docker-compose.*.yml` for SQLite and persistent media.
2. Run migrations and `python manage.py seed_demo` (or `import_legacy_data --seed-demo-user`) to create the `demo@shawon.me` admin user.
3. Import existing MySQL data and student photos via `python manage.py import_legacy_data --sql-file dump.sql --uploads-dir ./old/public/uploads` (or via the Unfold Admin Import UI).
