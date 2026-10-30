## 1. Scaffold Cookiecutter Django Project & SQLite Docker Stack

- [x] 1.1 Generate Cookiecutter Django project (`project_name="Web Result"`, `project_slug="web_result"`, `username_type="email"`, `use_docker="y"`, `use_whitenoise="y"`) directly into `/Users/mshawon/Developer/web-result` alongside `./old`
- [x] 1.2 Configure SQLite with WAL mode (`journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=20000`, `foreign_keys=ON`, `transaction_mode=IMMEDIATE`) in `config/settings/base.py`, `local.py`, and `production.py` storing the database at `data/db.sqlite3` (`/app/data/db.sqlite3` in Docker)
- [x] 1.3 Update `docker-compose.local.yml`, `docker-compose.production.yml`, and `compose/{local,production}/django/` entrypoints and Dockerfiles to remove PostgreSQL services/waits and mount persistent `sqlite_data` (`/app/data`) and `django_media` (`/app/web_result/media`) volumes

## 2. Academic Domain Models & Migrations

- [x] 2.1 Create the `web_result.results` Django app with `Semester`, `Course`, `Student`, `StudentCourse`, and `Result` models matching the legacy MySQL tables (`semesters`, `courses`, `students`, `course_student`, `results`) and column names (`semester_id`, `student_id`, `course_id`)
- [x] 2.2 Configure `MEDIA_URL = "/uploads/"` and `/uploads/` + `/media/` serving so `Student.image` (`images/<filename>`) URLs match the legacy application and work in both local and production Docker modes
- [x] 2.3 Generate and apply initial database migrations for `users` and `results` apps against the SQLite database

## 3. Django Unfold Admin, Import/Export & Locked-Down Auth

- [x] 3.1 Install and configure `django-unfold` (`unfold`, `unfold.contrib.filters`, `unfold.contrib.forms`, `unfold.contrib.inlines`, `unfold.contrib.import_export`) and `django-import-export` in `config/settings/base.py` (`INSTALLED_APPS` and `UNFOLD` settings)
- [x] 3.2 Update `web_result/users/admin.py` to register `User`, `Group`, `Site` (`django.contrib.sites`), and `allauth` models (`EmailAddress`) with `unfold.admin.ModelAdmin` and Unfold's `UserChangeForm`, `UserCreationForm`, and `AdminPasswordChangeForm`
- [x] 3.3 Create `ModelResource` and `(unfold.admin.ModelAdmin, ImportExportModelAdmin)` classes in `web_result/results/admin.py` for `Semester`, `Course`, `Student`, and `Result` with Unfold's `ImportForm` and `ExportForm`, image previews, search/filter fields, and full delete support
- [x] 3.4 Lock down authentication (`ACCOUNT_ALLOW_REGISTRATION = False`) so public registration is disabled while email login, logout, profile update, and password change work, and seed the default demo admin user (`demo@shawon.me` / `demo1234`)

## 4. Public Student Result Verification Portal (`/`)

- [x] 4.1 Port the public guest layout and search page (`GET /`) in `web_result/results/views.py` and templates with the exact Tailwind CSS + Figtree/Montserrat dark/light card layout, `student_id` and `date_of_birth` inputs, and validation error display
- [x] 4.2 Port the public student result verification view (`POST /`) displaying the student's uploaded photo (`/uploads/...`), profile fields (`Name`, `Student ID`, `Department`, `Session`, `Date of Birth`, `CGPA`, `Date of Issue`), and the `Course` / `Semester` / `GPA` table (with `select_related` to prevent N+1 queries)

## 5. Legacy MySQL Data & Uploaded Media Migration

- [x] 5.1 Implement the `python manage.py import_legacy_data` management command supporting `--sql-file` (MySQL `INSERT INTO` dump parser), `--mysql-url` (live MySQL connection), `--uploads-dir` (copying legacy uploaded images into `MEDIA_ROOT`), and `--seed-demo-user`

## 6. Verification & Automated Testing

- [x] 6.1 Write comprehensive pytest tests covering `Semester`, `Course`, `Student`, and `Result` models, public result verification (`GET /` and `POST /`), Unfold Admin registration and rendering for all built-in and custom models, `django-import-export` resources, and `import_legacy_data` (SQL dump + media file migration)
- [x] 6.2 Run the test suite, verify zero system check issues (`manage.py check`), and verify the application and Unfold Admin pages render cleanly
