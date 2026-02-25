# Snowflake Change Management with GitHub Actions

This repo automates Snowflake schema changes across DEV, QA, and PROD using GitHub Actions and `snowflake-connector-python`.

## Structure
- `changes/dev|qa|prod/` → Environment-specific SQL migrations
- `environments/*.yml` → Configs for each environment
- `migrations/000_create_history_table.sql` → Bootstrap history table
- `scripts/log_change.py` → Applies migrations and logs them into `schema_change_history`
- `.github/workflows/ci-cd.yml` → GitHub Actions pipeline

## Required Secrets
- SNOWFLAKE_ORG_DEV / QA / PROD
- SNOWFLAKE_ACCOUNT_DEV / QA / PROD
- SNOWFLAKE_USER_DEV / QA / PROD
- SNOWFLAKE_ROLE_DEV / QA / PROD
- SNOWFLAKE_AUTHENTICATOR_DEV / QA / PROD
- SNOWFLAKE_PRIVATE_KEY_DEV / QA / PROD

## Flow
1. Push to `dev` → applies DEV migrations.
2. Push to `qa` → applies QA migrations.
3. Push to `main` → applies PROD migrations.
4. Every migration is logged in `schema_change_history` for auditability.
