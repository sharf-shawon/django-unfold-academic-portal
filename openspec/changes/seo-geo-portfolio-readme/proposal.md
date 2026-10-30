## Why

The default Cookiecutter Django `README.md` only contains generic boilerplate and does not reflect the `django-unfold-academic-portal` architecture, the 2-prompt Spec-Driven AI migration from Laravel 11 to Django 6, the WAL-mode SQLite + media backup engine, or the zero-configuration Coolify deployment setup. A comprehensive, SEO- and GEO-optimized `README.md` is needed both to showcase full-stack and AI-native engineering skills in a public open-source portfolio and to serve as an authoritative reference for future developers and AI coding agents.

## What Changes

- Replace the generic [`README.md`](file:///Users/mshawon/Developer/web-result/README.md) with a comprehensive, SEO- and GEO-optimized portfolio and developer/agent reference document titled around **`django-unfold-academic-portal`**.
- Include an **Executive Summary (GEO Entity Block)** and **Recommended GitHub Repository Metadata** (slug `django-unfold-academic-portal`, description, and 20 targeted GitHub topics).
- Document the **2-Prompt Spec-Driven AI Engineering Case Study** (`OpenSpec` + `Context7` MCP + deterministic `pytest`/`ruff` verification) showing how the entire Laravel 11 + MySQL application in `./old` was ported to Cookiecutter Django 6 + Unfold Admin + WAL SQLite + Coolify Docker in two prompts.
- Document all **Full-Stack Features & Architecture**:
  - Public Student Result Verification Portal (`GET /`, `POST /`) with Tailwind CSS.
  - Unified **Django Unfold** Admin (`unfold`, `unfold.contrib.import_export`, `unfold.contrib.filters`, `unfold.contrib.forms`, `unfold.contrib.inlines`) covering all Academic models (`Semester`, `Course`, `Student`, `StudentCourse`, `Result`) and all Cookiecutter Django system models (`User`, `Group`, `Site`, `EmailAddress`, `SocialAccount`, `SocialToken`, `SocialApp`).
  - Dual-Engine Legacy MySQL & Media Migration (`python manage.py import_legacy_data` CLI + `django-import-export` Admin UI).
  - High-Concurrency Production SQLite (`journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=20000`, `IMMEDIATE` transactions).
  - Online WAL-Safe SQLite + Media Backup & Restore (`python manage.py backup_data` using `sqlite3.Connection.backup()`, automatic pre-migration backups, periodic background daemon, and retention pruning).
  - Zero-Config One-Click **Coolify** Deployment (`/docker-compose.yaml`, `SERVICE_FQDN_DJANGO_5000`, `SERVICE_BASE64_64_DJANGO`, dynamic `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`, SSL-exempt `/healthz/` probe, and persistent volumes).
- Include **Developer & AI Agent Reference** sections (directory layout, management commands, environment variables table, testing/linting commands, and OpenSpec workflow conventions) plus **Mermaid architecture/ER diagrams** and an **SEO/GEO FAQ**.

## Capabilities

### New Capabilities
<!-- None — documentation-only change with skip_specs: true -->

### Modified Capabilities
<!-- None — documentation-only change with skip_specs: true -->

## Impact

- [`README.md`](file:///Users/mshawon/Developer/web-result/README.md)
- [`web_result/results/tests/test_results.py`](file:///Users/mshawon/Developer/web-result/web_result/results/tests/test_results.py) (add a verification test ensuring `README.md` documents key portfolio, backup, and Coolify reference sections)
