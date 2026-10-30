## Why

The historic Laravel 11 Academic Results Management System (`./old`) needs to be ported from scratch to a modern, maintainable Cookiecutter Django application in the repository root (`/Users/mshawon/Developer/web-result`). By moving to Django with SQLite, Docker, `django-unfold`, and `django-import-export`, we eliminate custom CRUD boilerplate, streamline production deployment with a lightweight single-database footprint, preserve the exact public student result verification experience, and seamlessly migrate existing MySQL records and student photos.

## What Changes

- **Cookiecutter Django + Docker + SQLite Foundation**: Scaffold a production-ready Cookiecutter Django project (`web_result`) directly in `/Users/mshawon/Developer/web-result` alongside `./old`, configured with Docker (`docker-compose.local.yml` and `docker-compose.production.yml`) and WAL-mode SQLite (`db.sqlite3` stored on a persistent Docker volume) instead of PostgreSQL.
- **Academic Results Domain Models**: Create 1-to-1 compatible Django models (`Semester`, `Course`, `Student`, `Result`) in `web_result/results` matching the legacy MySQL schema (`semesters`, `courses`, `students`, `course_student`, `results`) so existing IDs, foreign keys, and fields work without transformation.
- **Django Unfold Admin + Import/Export**: Install and configure `django-unfold` (`unfold` and `unfold.contrib.import_export`) and `django-import-export` to provide a unified, modern admin interface for both built-in Cookiecutter Django models (`User`, `Group`, `Site`, `EmailAddress` from `allauth`) and the new academic models (`Semester`, `Course`, `Student`, `Result`), including full CRUD (fixing the missing Course delete behavior from `./old`) and browser-based CSV/JSON/XLSX import/export.
- **Locked-Down Authentication & Demo Seeding**: Use Cookiecutter Django's email-based `User` model with public registration disabled (`ACCOUNT_ALLOW_REGISTRATION = False`), supporting login, logout, profile updates, and password changes, plus a seeded demo admin account (`demo@shawon.me` / `demo1234`).
- **Public Student Result Verification Portal (`/`)**: Replicate the exact layout, styling (Tailwind CSS + Montserrat/Figtree dark/light card aesthetic), and behavior of the legacy public verification portal (`GET /` search by `student_id` and `date_of_birth`, `POST /` displaying student profile, photo, CGPA, and course/semester/GPA table).
- **Legacy Data & Uploaded Media Migration (`import_legacy_data`)**: Provide a `python manage.py import_legacy_data` management command that imports legacy records from either a MySQL `.sql` dump file (`--sql-file`) or a live MySQL connection (`--mysql-url`), and migrates/copies legacy uploaded student images (`uploads/images/...`) so student photos render seamlessly on the public verification page and in Django Unfold Admin.

## Capabilities

### New Capabilities
- `cookiecutter-sqlite-docker`: Cookiecutter Django project scaffold in the repository root configured for local and production Docker execution using persistent WAL-mode SQLite and persistent media storage.
- `academic-models-and-unfold-admin`: `Semester`, `Course`, `Student`, and `Result` models plus comprehensive `django-unfold` and `django-import-export` configuration covering all new models and all existing Cookiecutter Django / `allauth` / `sites` / `auth` models, along with locked-down authentication.
- `public-result-verification`: Public student result search and verification views (`GET /` and `POST /`) matching the legacy layout, validation rules, dark/light styling, and student image rendering.
- `legacy-data-and-media-migration`: CLI management command (`import_legacy_data`) and media migration utilities for importing historic MySQL dumps/connections (`semesters`, `courses`, `students`, `course_student`, `results`) and copying uploaded student images (`uploads/images/`).

### Modified Capabilities

## Impact

- **Repository Root (`/Users/mshawon/Developer/web-result`)**: Adds Cookiecutter Django project structure (`manage.py`, `pyproject.toml`, `config/`, `web_result/`, `compose/`, `docker-compose.local.yml`, `docker-compose.production.yml`, `.envs/`) while keeping `./old` intact as the reference/source project.
- **Dependencies**: Django, `django-environ`, `django-allauth`, `django-unfold`, `django-import-export`, `Pillow`, `whitenoise`, `gunicorn`/`uvicorn`.
- **Database & Storage**: Uses SQLite (`/app/data/db.sqlite3` in Docker, `data/db.sqlite3` locally) with WAL mode enabled, and serves uploaded student photos at `/uploads/` (and `/media/`) for backward compatibility with legacy `images/<filename>` paths.
