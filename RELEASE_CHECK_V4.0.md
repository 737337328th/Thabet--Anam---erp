# ثابت أنعم ERP V4.0 — Release Gate

## Release principle
V4.0 is a stability release. A version is considered releasable only after compile checks, automated tests, ZIP integrity validation, and a database integrity scan on startup/test data.

## Included hardening
- Application version 4.0.0.
- Public minimal health endpoint without database details.
- Manager-only full integrity scan for journals, accounts, orphan journal lines, purchase totals, invoice overpayments, and overlapping fiscal periods.
- Fiscal-year close rejects overlapping accounting periods.
- Date-range validation for expense reports.
- Existing authentication, rate limiting, production secret guard, audit logging, and permission controls retained.

## Known non-blocking warnings
FastAPI `on_event` deprecation warnings may appear in the current codebase. They do not fail the release gate; migration to lifespan is a follow-up maintenance task.
