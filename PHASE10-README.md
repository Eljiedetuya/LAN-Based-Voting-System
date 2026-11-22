# Phase 10 — React + Django integration

This package is based on the previous Phase 9 artifact. **Merge into the working local project after taking a backup; do not overwrite `.env`, existing migrations, or local changes.**

## What is connected

- Django session + CSRF login, logout, current-user verification
- Role-aware frontend routes (backend permission enforcement remains authoritative)
- Student election list, candidate data, temporary ballot selections, review, atomic backend submission, status-based confirmation
- Admin election creation/editing/open/close, position creation, candidate creation/edit, voter creation, eligibility assignment
- Admin closed results, audit log listing, aggregate participation and system health
- Monitor read-only election selector, participation, status, results (closed only), and health
- Five-second polling on monitoring pages, paused for background tabs

## Small backend API addition

- `GET /api/monitoring/elections/`: read-only `{id,title,status}` for admin and monitor roles; no management permission granted.
- `CandidateSerializer` now exposes `election_id` read-only for editing forms.
- Backend test added for monitoring election-list permissions.

## Local run (after merging)

1. Backend PowerShell terminal: activate its existing `.venv`, run `python manage.py check`, `python manage.py showmigrations`, `python manage.py test`, then `python manage.py runserver 127.0.0.1:8000`.
2. Frontend PowerShell terminal: `cd frontend`, `npm install`, `npm run test:api`, then `npm run dev`.
3. Open `http://127.0.0.1:5173` for **test accounts and synthetic ballots only**. First sign in as an existing user (there is no demo role switcher anymore).
4. For local HTTP testing, both Django session and CSRF cookies must have their secure flags disabled in local `backend/.env`. In a final school LAN deployment, use trusted HTTPS and turn the secure flags on.
5. For LAN verification, follow `docs/PHASE10-INTEGRATION-TEST-PLAN.md`.

## Testing performed in the preparation workspace

- Python compilation and JSX syntax/import scans passed.
- Five Node-based API client tests passed (request shape, cookies, duplicate 409, network uncertainty, missing CSRF).
- No Django/MySQL runtime or Vite production build could be executed here due missing dependencies and an unavailable package registry.

## Remaining work

- Execute Django test suite on your own MySQL test database and run the complete integration checklist.
- Verify React production build and browser/mobile/keyboard behavior.
- Extend voter-list pagination if school enrollment grows beyond the 100-account page size.
- Implement reports and settings only after corresponding backend API contracts are approved.
- Add a server-authoritative closing timestamp before integrating a countdown.
- Configure HTTPS with local certificate trust before handling actual student credentials.
