# Recommended feature enhancements — before Phase 11 QA

This update is built on the Phase 10 project. Back up your **working local project** before merging. The archive is a snapshot of the supplied Phase 10 package, not your local modifications.

## Added

- `GET /api/monitoring/integrity/{election_id}/` administrator-only aggregate ballot/participation reconciliation; reports count mismatches, missing selections, and invalid candidate/position associations. No individual ballot or voter association is returned.
- `GET /api/reports/{election_id}/csv/` administrator/monitor-only downloadable CSV report, only after election closes and integrity checks pass. Spreadsheet formula injection precautions included.
- `/admin/integrity` frontend page; `/admin/reports` with CSV download. No fictional data.
- Separate classroom UDP discovery Python utility and networking protocol demonstration guide. The discovery utility **does not interact with voting**, provide security, or authenticate the server.
- Django tests in `backend/results/tests.py` for permissions, closed-only export, reconciliation, and privacy of CSV output.

## Already present in Phase 10

- Live turnout dashboard polling every 5 seconds
- Audit logs, session login, role authorization
- Django/MySQL application health checks
- Database-backed election results behind closed-election permissions

## Not implemented in this incremental enhancement

- Automatic election closing / countdown (requires approved database model field, migration, server-side deadline policy)
- Bulk voter CSV import (needs a safe preview/validation and credential-provisioning workflow)
- Connected-client monitoring and aggregate traffic collection (would require approved telemetry retention limits)
- Persistent network packet capture (intentionally NOT added; use Wireshark separately on test devices)

## Local development verification

From the existing project folder (with configured MySQL, `.env` and Python virtual environment):

```
cd backend
python manage.py check
python manage.py test results
python manage.py test
```

From `frontend`:

```
npm install
npm run build
npm run test:api
npm run dev
```

Log in as ADMIN and check `/admin/integrity` and `/admin/reports`, first with a closed **synthetic** election and then an Open one. Ensure reports are denied for Open elections. Use a MONITOR account to verify report access and deny integrity endpoint access. Use a STUDENT account to verify denial of both endpoints. Test from a LAN client over the intended local origin.

**No new Django model fields or database migrations are introduced by this package.** Do not replace your existing database, local `.env` or migration history. The Phase 6 composite foreign key migrations remain a separate unverified requirement.

**Security note:** Reconciliation checks validate aggregate consistency but do not prove the absence of privileged database tampering or guarantee anonymous voting. Run QA before any use beyond synthetic school demonstration.
