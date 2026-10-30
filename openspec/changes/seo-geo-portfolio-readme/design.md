## Context

See `proposal.md` for motivation. The repository is being published under the name **`django-unfold-academic-portal`** as an open-source full-stack and AI-native engineering portfolio showcase and developer/agent reference.

## Goals / Non-Goals

**Goals:**
- Maximize **Search Engine Optimization (SEO)** for GitHub/Google and **Generative Engine Optimization (GEO)** for LLM retrieval engines (Perplexity, ChatGPT Search, Gemini, Claude) using structured entity summaries, comparison tables, Mermaid diagrams, and long-tail FAQ headings.
- Showcase how the entire Laravel 11 + MySQL application (`./old`) was ported to Cookiecutter Django 6 + Django Unfold + WAL SQLite + Coolify Docker in **2 prompts** using Spec-Driven AI Development (`OpenSpec`) and real-time documentation grounding (`Context7`).
- Provide complete, actionable operational documentation for future developers and AI coding agents covering features, database schema, legacy data migration (`import_legacy_data`), online WAL-safe backups (`backup_data`), and zero-config Coolify deployment (`/docker-compose.yaml`).

**Non-Goals:**
- Modifying runtime application behavior or database models.

## Decisions

### 1. Dual-Purpose Structure: Portfolio Showcase + Developer/AI Agent Reference
- **Decision**: Organize `README.md` into two complementary halves:
  1. **Portfolio & AI Engineering Case Study** (Hero badges, GEO Executive Summary, 2-Prompt Spec-Driven Migration breakdown, Laravel-to-Django Architecture Comparison Table, Mermaid ER & Deployment diagrams).
  2. **Operational & AI Agent Reference** (Feature catalog, Coolify one-click deployment & magic variables, online WAL SQLite + media backup/restore commands, legacy MySQL/media migration guide, environment variable matrix, and OpenSpec directory reference).
- **Rationale**: Satisfies both human/LLM portfolio evaluators and future developers or AI agents working inside the repository.

## Risks / Trade-offs

- **[Risk] Documentation drift over time** → **Mitigation**: Add a test in `web_result/results/tests/test_results.py` asserting that `README.md` retains key reference sections (`django-unfold-academic-portal`, `import_legacy_data`, `backup_data`, `SERVICE_FQDN_DJANGO_5000`, `/healthz/`).
