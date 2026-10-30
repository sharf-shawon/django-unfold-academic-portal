# public-result-verification Specification

## Purpose

Provides the public student result search and verification portal (`GET /` and `POST /`) replicating the layout, styling, student photo display, and behavior of the legacy Laravel application.

## Requirements

### Requirement: Public student result search page (`GET /`)
The system SHALL render the public student result verification form at `GET /` using the centered card guest layout (Tailwind CSS + Figtree/Montserrat dark/light theme) with required inputs for `Student ID` (`student_id`) and `Date of Birth` (`date_of_birth`) and a `Search Result` submit button.

#### Scenario: Visiting the home page
- **WHEN** an unauthenticated visitor requests `GET /`
- **THEN** the system responds with HTTP 200 and renders the centered card form containing `student_id` and `date_of_birth` fields

### Requirement: Public student result verification (`POST /`)
The system SHALL validate `student_id` and `date_of_birth` submitted via `POST /` and display the matching student's verification page with their uploaded photo (if present), `Name`, `Student ID`, `Department`, `Session`, `Date of Birth`, `CGPA`, `Date of Issue`, and a table of `Course` (`code`), `Semester` (`name`), and `GPA` (`gpa`) when results exist.

#### Scenario: Valid student ID and date of birth with results
- **WHEN** a visitor submits `POST /` with a `student_id` and matching `date_of_birth`
- **THEN** the system renders the student verification card, displays the student image (when set), and renders the course/semester/GPA results table (or hides the table if the student has no results)

#### Scenario: Unknown student ID or mismatched date of birth
- **WHEN** a visitor submits `POST /` with a `student_id` that does not exist or a `date_of_birth` that does not match the student record
- **THEN** the system returns a validation error on the search form (when `student_id` does not exist or inputs are invalid) or HTTP 404 when `student_id` exists but `date_of_birth` does not match, matching the legacy behavior
