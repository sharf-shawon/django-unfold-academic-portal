## Purpose

Provides CLI and media migration capabilities to import legacy MySQL data (`semesters`, `courses`, `students`, `course_student`, `results`) and migrate user-uploaded student images (`uploads/images/...`) so legacy records and pictures work out of the box.

## ADDED Requirements

### Requirement: Legacy MySQL data import command (`import_legacy_data`)
The system SHALL provide a `python manage.py import_legacy_data` management command that imports `semesters`, `courses`, `students`, `course_student`, and `results` (while skipping `users`) from either a MySQL `.sql` dump file (`--sql-file`) or a live MySQL database URL (`--mysql-url` / `LEGACY_MYSQL_URL`), preserving primary keys and foreign keys idempotently.

#### Scenario: Importing from a MySQL dump file
- **WHEN** an operator runs `python manage.py import_legacy_data --sql-file <path>`
- **THEN** the system parses the `INSERT INTO` rows for `semesters`, `courses`, `students`, `course_student`, and `results`, upserts them in foreign-key dependency order inside a transaction, and preserves all record IDs

### Requirement: Legacy uploaded student image migration and URL compatibility
The system SHALL support migrating existing uploaded student images (e.g., via `--uploads-dir <path>` on `import_legacy_data` defaulting to `./old/public/uploads` when present) into the Django media storage root and serve uploaded files at `/uploads/<path>` (as well as `/media/<path>`) so legacy `images/<filename>` values on `Student.image` resolve without broken links.

#### Scenario: Migrating and rendering legacy student images
- **WHEN** a legacy `Student` record has `image = "images/photo.jpg"` and files are migrated from `./old/public/uploads` (or a specified `--uploads-dir`)
- **THEN** the file is copied to `<MEDIA_ROOT>/images/photo.jpg` and requests to `/uploads/images/photo.jpg` return the image on both the public verification page and in Django Unfold Admin
