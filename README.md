# Snowflake Change Management with GitHub Actions

This repo automates Snowflake schema changes across DEV, QA, and PROD using [snowflakechange](https://pypi.org/project/snowflakechange/).

## Structure
- `changes/dev|qa|prod/` → Environment-specific SQL migrations
- `environments/*.yml` → Configs for each environment
- `migrations/000_create_history_table.sql` → Bootstrap history table
- `scripts/log_change.py` → Logs applied migrations into `schema_change_history`
- `.github/workflows/ci-cd.yml` → GitHub Actions pipeline

## Flow
1. Push to `dev` → applies DEV migrations.
2. Push to `qa` → applies QA migrations.
3. Push to `main` → applies PROD migrations.
4. Every migration is logged in `schema_change_history` for auditability.
