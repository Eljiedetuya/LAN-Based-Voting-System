# Phase 9 — Backend verification checklist

**Status:** Static syntax inspected only; Django/MySQL runtime verification required on your computer.

1. Run `python manage.py check` with local environment variables.
2. Use a **new development database** for initial custom-user migrations.
3. Run `makemigrations`, inspect generated models and SQL, then `migrate`.
4. Run `python manage.py test` and resolve failures before proceeding.
5. Test login, logout, CSRF rejection and role permission denial via HTTP client.
6. Create an election, positions, candidates and eligibility before opening.
7. Verify that a second election cannot be opened while one is Open.
8. Submit a complete valid ballot and verify the confirmation contains **no selections or ballot ID**.
9. Submit a duplicate and verify exactly one accepted ballot and one voted flag.
10. Run the MySQL concurrency test and a 100-user load test against a disposable dataset.
11. Verify invalid candidates, duplicated positions, missing positions and cross-election selections are rejected with no partial rows.
12. Close election concurrently with a vote; verify correct transaction ordering.
13. Verify post-closure results match known ballots; results API must reject Open status.
14. Verify student and monitor requests cannot perform administrative writes.
15. Verify no direct voter identity exists on ballot tables or in auditing/logging of ballot submissions.
16. Verify aggregate statistics do not expose candidate totals while voting is Open.
17. Test database restart, backup and controlled restore in a disposable environment.
18. Validate HTTPS and local LAN firewall settings before any real student credentials are used.
