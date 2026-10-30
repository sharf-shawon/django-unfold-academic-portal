## Purpose

Defines the academic domain data models (`Semester`, `Course`, `Student`, `Result`), locked-down email authentication, and the unified `django-unfold` + `django-import-export` admin interface covering both built-in Cookiecutter Django models and academic models.

## ADDED Requirements

### Requirement: Legacy-compatible academic domain models
The system SHALL provide `Semester`, `Course`, `Student`, and `Result` models mapped to legacy table and column names (`semesters`, `courses`, `students`, `course_student`, `results`) with full validation:
- `Semester`: `name` (max 20 chars), `year` (4-digit string), `created_at`, `updated_at`.
- `Course`: `name` (max 255 chars), `code` (max 255 chars), `semester` (FK to `Semester` via `semester_id`), `created_at`, `updated_at`.
- `Student`: `student_id` (unique roll/ID string), `name`, `email` (unique), `phone`, `address`, `session`, `department`, `date_of_birth`, `date_of_issue`, `cgpa` (0.00 to 4.00), `image` (optional image uploaded to `images/`), `courses` (M2M to `Course` via `course_student`), `created_at`, `updated_at`.
- `Result`: `student` (FK to `Student` via `student_id`), `course` (FK to `Course` via `course_id`), `gpa` (0.00 to 4.00), `created_at`, `updated_at`.

#### Scenario: Creating and deleting academic records
- **WHEN** an administrator creates, edits, or deletes a `Semester`, `Course`, `Student`, or `Result`
- **THEN** the system persists the changes in the corresponding database table and supports deleting `Course` records cleanly

### Requirement: Django Unfold support for all existing and new models
The system SHALL use `django-unfold` as the admin theme and register all active admin models using `unfold.admin.ModelAdmin`, including built-in and Cookiecutter Django models (`User`, `Group`, `Site`, and `allauth` `EmailAddress` / social account models if enabled) as well as `Semester`, `Course`, `Student`, and `Result`.

#### Scenario: Rendering built-in and custom models in Unfold Admin
- **WHEN** an authenticated staff/admin user visits `/admin/` and navigates to changelist, add, edit, or password-change pages for `User`, `Group`, `Site`, `EmailAddress`, `Semester`, `Course`, `Student`, or `Result`
- **THEN** every page renders with `django-unfold` styling and forms (`UserChangeForm`, `UserCreationForm`, `AdminPasswordChangeForm`) without unstyled fallback pages or template errors

### Requirement: Browser import and export via django-import-export
The system SHALL integrate `django-import-export` with `unfold.contrib.import_export` (`ImportForm`, `ExportForm`) on `Semester`, `Course`, `Student`, and `Result` admin views so administrators can import and export records in CSV, JSON, or XLSX formats via the browser.

#### Scenario: Admin CSV/JSON import and export
- **WHEN** an administrator clicks Import or Export on the `Semester`, `Course`, `Student`, or `Result` admin changelist
- **THEN** the system renders Unfold-styled import/export forms and imports or exports rows matching the legacy column names (`id`, `semester_id`, `course_id`, `student_id`, etc.)

### Requirement: Locked-down email authentication and seeded demo admin
The system SHALL authenticate users by email and password, disable public self-registration (`ACCOUNT_ALLOW_REGISTRATION = False`), allow authenticated users to update their profile name/email and password, and provide a seeded demo admin user (`demo@shawon.me` / `demo1234`).

#### Scenario: Demo admin login and disabled public signup
- **WHEN** a user logs in with `demo@shawon.me` and `demo1234`
- **THEN** authentication succeeds with admin access, while unauthenticated requests to signup endpoints are rejected or disabled
