# Phase 10 — local integration test plan

**Scope:** Run on a disposable MySQL development database with synthetic accounts. This archive has not been tested against the user's Windows/MySQL environment. Do not test with real students before authentication, security and privacy review.

## Before testing

1. Back up your current working project and database. The ZIP comes from the Phase 9 project artifact; preserve any newer local changes when merging.
2. Make sure Django, Vite and MySQL all run successfully on the intended local computer.
3. Confirm `backend/.env` exists locally (the archive does not contain it) and use the existing working database connection.
4. Check the backend: `python manage.py check`, `python manage.py showmigrations`, `python manage.py test`. Do **not** reset an existing database to make migrations pass.
5. Start Django `python manage.py runserver 127.0.0.1:8000`. Start Vite in the frontend with `npm install` and `npm run dev`.
6. Login with real *test accounts* created using Django's account tools. A monitor account must have role MONITOR; an admin must have role ADMIN; students require role STUDENT and student_id.
7. Browser and Django must use compatible local addresses. With Vite at `localhost:5173`, add `localhost` to Django allowed hosts and configure HTTP-only **for local synthetic-data testing** (`DJANGO_SESSION_COOKIE_SECURE=False`, `DJANGO_CSRF_COOKIE_SECURE=False`). For school demonstrations with real credentials, use trusted HTTPS instead.

## End-to-end checklist

| ID | Procedure | Expected result |
|---|---|---|
| INT-01 | Login as student from React | Django session established; student landing page shown |
| INT-02 | List student elections | Only eligible OPEN elections shown |
| INT-03 | Open candidates | Correct positions and candidates retrieved from DB |
| INT-04 | Make a selection for each position | Review enabled only when complete |
| INT-05 | Go back from review and edit | Selections preserved in temporary React state |
| INT-06 | Submit a valid ballot | Exactly one accepted ballot; server response recorded; confirmation reload verifies status |
| INT-07 | Resubmit or use second browser tab | Server rejects duplicate; ballots do not double-count |
| INT-08 | Reload confirmation direct URL with no vote | No false positive confirmation |
| INT-09 | Login as admin, create Draft election | New election persisted |
| INT-10 | Add positions, candidates, eligible student | Election configuration present before opening |
| INT-11 | Open configured election | State changes to OPEN on server; voter sees election |
| INT-12 | Monitor participation from another account | Counts update with five-second polling |
| INT-13 | Close election | Voter submission blocked; results API accessible only to admin/monitor |
| INT-14 | Access `/admin/elections` as student | React blocks navigation and Django rejects API operation |
| INT-15 | Login as monitor | No management controls; monitor election list and health display |
| INT-16 | Disconnect Wi-Fi while submitting | Client says outcome uncertain and requires status check; no false success |
| INT-17 | Expire authenticated session | Client returns to session-expired page after protected API denial |
| INT-18 | Simultaneous clients (10/25/50/100) | Test measured latency and verify exact counts, no duplicate acceptance |
| INT-19 | Turn external internet off | Website, React assets, login, API, MySQL operate on local LAN |
| INT-20 | Open LAN site from smartphone | Same-origin API requests work and mobile layout remains usable |

**Important:** INT-06, INT-07, INT-13 and INT-18 require direct MySQL reconciliation and the backend's transaction tests. UI checks alone are insufficient. If a submission returns a timeout, do not resubmit until the voter status is confirmed.

## Known limitations

- Reports and portal-settings APIs do not exist in Phase 9; frontend routes show unavailable notices.
- Election countdown is unavailable because no authoritative scheduled closing timestamp is provided by the backend.
- MySQL health endpoint reports service reachability, not router traffic or connected-device counts.
- Voter list is paginated with `page_size=100`, matching the approved 50–100 voter range. More than 100 users or wider search functionality requires full pagination.
- Phase 6 composite SQL foreign keys were not all implemented in Phase 9. Backend candidate/position validation must be retained and direct DB modifications restricted.
- No certified election-security guarantees or formal browser accessibility audit are claimed.

## Environment-specific deployment note

For a *synthetic-data LAN development test only*: `npm run dev:lan` serves Vite from a LAN interface (ensure the Vite CLI host override is effective). Django can remain on `127.0.0.1:8000`, proxied via Vite. Set `DJANGO_ALLOWED_HOSTS` to include the Vite-accessed server LAN IP and verify CSRF Origin settings, for example `DJANGO_CSRF_TRUSTED_ORIGINS=http://192.168.10.10:5173` when that is the actual local address. Windows firewall should allow the frontend test port only on the approved Private LAN. Never expose MySQL to student devices. For a real school election, use built React assets, a local HTTPS reverse proxy and properly trusted certificates, not Django/Vite development servers.
