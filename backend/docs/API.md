# Phase 9 REST API Contract (Draft implementation)

All endpoints are same-origin and require session authentication except `GET /api/health/`, `GET /api/auth/csrf/`, and `POST /api/auth/login/`. All state-changing browser requests require Django CSRF protection.

| Method | URL | Role | Purpose |
|---|---|---|---|
| GET | `/api/auth/csrf/` | Public | CSRF cookie |
| POST | `/api/auth/login/` | Public | `{username,password}` |
| POST | `/api/auth/logout/` | Authenticated | End session |
| GET | `/api/auth/me/` | Authenticated | Own role/account |
| GET/POST | `/api/admin/voters/` | Admin | List/create student accounts |
| GET/PATCH | `/api/admin/voters/{id}/` | Admin | View/update student |
| GET/POST | `/api/admin/elections/` | Admin | List/create |
| GET/PATCH | `/api/admin/elections/{id}/` | Admin | View/update draft |
| POST | `/api/admin/elections/{id}/open/` | Admin | Open election |
| POST | `/api/admin/elections/{id}/close/` | Admin | Close election |
| GET/POST | `/api/admin/elections/{id}/positions/` | Admin | List/create positions |
| GET/PATCH/DELETE | `/api/admin/positions/{id}/` | Admin | Draft position changes |
| GET/POST | `/api/admin/candidates/` | Admin | List/create candidates |
| GET/PATCH/DELETE | `/api/admin/candidates/{id}/` | Admin | Draft candidate changes |
| GET/POST/DELETE | `/api/admin/elections/{id}/eligibility/` | Admin | Manage eligible voters in Draft |
| GET | `/api/elections/active/` | Student | Eligible open elections |
| GET | `/api/elections/{id}/candidates/` | Student | Candidate info |
| GET | `/api/elections/{id}/my-status/` | Student | Own participation |
| POST | `/api/elections/{id}/submit-vote/` | Student | Atomic vote |
| GET | `/api/results/{id}/` | Admin/Monitor | Closed-only totals |
| GET | `/api/monitoring/participation/?election_id={id}` | Admin/Monitor | Turnout aggregate |
| GET | `/api/monitoring/health/` | Admin/Monitor | Sanitized service health |
| GET | `/api/admin/audit-events/` | Admin | Paginated audit events |

## Submit ballot

`POST /api/elections/1/submit-vote/`

```json
{"selections":[{"position_id":1,"candidate_id":2},{"position_id":3,"candidate_id":4}]}
```

Accepted `201` response:

```json
{"status":"recorded","election_id":1,"has_voted":true}
```

No internal ballot ID or chosen candidates are returned. Duplicate or closed-election requests return HTTP 409. Invalid candidate/position returns HTTP 400. Network timeouts are an **unknown outcome**; use the own-status endpoint before any new attempt.

## Privacy and known limitations

The application schema contains no direct identity-to-ballot foreign key. Ballot completeness and cross-election candidate checks are performed in the transaction service. This implementation does not use the SQL composite foreign keys from the Phase 6 reference; direct privileged database writes could bypass those business validations. The system is a school prototype, not a certified anonymous election platform.
