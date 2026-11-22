# Phase 8 — React UI implementation

This frontend is **a design prototype**. It deliberately does not implement real voting or authentication.

## Run

In `frontend/`:

```sh
npm install
npm run dev
```

Open http://127.0.0.1:5173 and choose a demo role. The configured `/api/health/` proxy points at the existing Django Phase 7 server on `127.0.0.1:8000`.

## Pages

- `/` role chooser, `/login`, `/unauthorized`, `/session-expired`
- `/student/dashboard`, `/student/elections`, `/student/candidates`, `/student/candidate-profile`, `/student/ballot`, `/student/review`, `/student/confirmation`, `/student/status`
- `/admin/dashboard`, `/admin/elections`, `/admin/elections/1/edit`, `/admin/candidates`, `/admin/candidates/new`, `/admin/candidates/:id/edit`, `/admin/voters`, `/admin/voters/add`, `/admin/monitoring`, `/admin/results`, `/admin/reports`, `/admin/audit`, `/admin/system`, `/admin/settings`
- `/monitor/dashboard`, `/monitor/participation`, `/monitor/election-status`, `/monitor/server-health`

## Deliberate limitations

- Demo role switcher is not authentication. Backend must enforce every authorization.
- All records, statuses, counts and candidate names are synthetic except the public `/api/health/` response.
- Final ballot submission, election mutations, voter import/account creation, settings saves and report exports are disabled.
- Provisional ballot choices exist in React memory only and disappear on reload.
- Dashboard counts are labeled mock and **not polled** until authenticated aggregate API endpoints exist.
- Countdown is a design placeholder showing a sample target date, not a promise of actual election closure.
- Do not use this project for real elections until authenticated backend and all verification gates pass.

## Verification

Run `npm run build` after installing dependencies. Inspect with keyboard-only navigation and verify screen widths 360, 768, 1280 pixels. Test the API health status with Django both online and offline. See `docs/PHASE8-TEST-PLAN.md` for manual cases.
