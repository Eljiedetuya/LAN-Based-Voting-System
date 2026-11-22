# Phase 9 — Django REST backend implementation

This folder extends the existing Phase 7 Django health-check project while preserving the Phase 8 React source. **The frontend still uses demo-only state; it has not been wired to this backend.** No production vote can be cast through the demo UI.

## What was added

- A custom `accounts.User` model (student, administrator, monitor).
- Election, position, candidate and voter-eligibility models.
- Anonymous UUID ballots and ballot-selection models with no identity/ballot foreign key.
- Django session login/logout with CSRF cookie endpoint; role-aware permissions.
- Administrator CRUD, lifecycle rules and audit events.
- Atomic vote submission protected by election-row and voter-eligibility-row locks.
- Closed-election tally endpoints, aggregate turnout, sanitized health endpoint.
- API descriptions in `docs/API.md` and automated test source.

## Before merging with your working Windows project

1. **Back up your current working Phase 7/8 project and MySQL database.** Do not replace local `.env` files, passwords, installed packages or React changes.
2. Merge these backend files into the same project. Do not replace the complete project folder blindly.
3. Create a **new empty development database** and a MySQL user with appropriate privileges for schema migration/testing. **Do not migrate the database from a previous Django user model blindly.** This phase introduces `AUTH_USER_MODEL = 'accounts.User'`, which must exist before your initial migrations. If you have already run migrations or have important data, stop and plan a safe migration instead of deleting anything.
4. Confirm `backend/.env` is set locally and untracked by Git; do not use the example placeholder credentials.
5. Install dependencies, generate migrations, and run Django checks and tests in a terminal that has MySQL and Django installed.

## Windows PowerShell setup / verification

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations accounts elections voting audit
python manage.py sqlmigrate accounts 0001
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver 127.0.0.1:8000
```

`sqlmigrate accounts 0001` assumes the generated first migration is named `0001_initial`; check the filename if Django chooses another name. If the database has existing migrations, **do not follow the migration commands unchanged**; first inspect the schema and migration history.

The MySQL user used for initial migrations must have schema creation privileges. After creating tables, use a lower-privilege runtime account for normal API operation.

### Example CSRF/session workflow

The React application should obtain `/api/auth/csrf/` first (with credentials), then send the `csrftoken` cookie value as `X-CSRFToken` for state-changing requests. The session cookie is HTTP-only. All same-origin requests use cookies; CORS is not enabled. Do not paste cookies or real student passwords into logs or troubleshooting screenshots.

## Required tests and limits

- `python manage.py check` and `python manage.py test` require Django and MySQL, and were **not run** in the generation workspace.
- MySQL service and DB migrations were **not run** in the generation workspace; package installation had no DNS/network access.
- `voting/test_concurrency.py` is a genuine multi-threaded MySQL integration test; success must be confirmed on your hardware. The election lock serializes all submissions within one election; test performance with 10/25/50/100 clients before live use.
- Django's ORM schema intentionally does **not** enforce the Phase 6 reference SQL composite ballot/candidate foreign keys; cross-election and wrong-position relationships are validated inside the voting service. If the database must reject even privileged direct SQL insertion of malformed selections, design and apply explicit MySQL constraints in a controlled follow-up migration. Do not claim that this is already implemented.
- Login throttling uses DRF's basic throttling as a starting safeguard; it is not a substitute for robust brute-force defense.
- No scheduled election close, CSV import, PDF export, UDP discovery service, or automatic browser API integration is included here.
- This is an academic prototype, not a certified election platform.

## Run-time safety

Use local-only access for development. Django `runserver` is not a production web server. For use with real student credentials, deploy HTTPS using a trusted local certificate and restrict MySQL to the server. Do not expose port 3306 to students.
