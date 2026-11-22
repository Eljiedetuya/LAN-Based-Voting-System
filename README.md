# LAN Voting System

A local development prototype for managing elections and recording student ballots over a LAN. The project includes a React frontend, a Django REST API, and a MySQL database.

> **Use synthetic accounts and ballots for development. This is an academic prototype, not a certified election system.** The included Django and Vite development servers use HTTP and are not suitable for a live school election. A real deployment needs a reviewed security design, trusted HTTPS for every device, operational procedures, and independent testing.

## Implemented features

### Student accounts and eligibility

- Session-based sign-in and sign-out with CSRF protection and role checks.
- Temporary passwords can be required to change at first sign-in.
- Student accounts include a student ID, name, course (BSIT or BIT), and year level (1–4).
- An administrator can add students and optionally assign them to a Draft election.
- Existing student details can be edited. Deactivate and reactivate actions preserve the account and election history; inactive accounts are hidden unless **Show inactive accounts** is selected. Deactivation is blocked for a student eligible in an open election.
- Election Setup provides group eligibility choices for all BSIT and BIT students, each full course, and each course/year group. A preview shows matching, already eligible, and newly added counts. The administrator confirms the assignment once. The server processes the entire group, regardless of voter-list pagination, and repeating the assignment does not create duplicates.

### Candidates and voting

- Administrators can create and edit Draft elections, positions, and candidates, then open or close an election.
- Candidate profile photos can be JPG/JPEG, PNG, or WebP, up to 2 MB. The API checks the image content, stores files under random names in `backend/media/`, and uses initials when a photo is missing. Photos are profile images only; the system does not identify people from faces.
- Eligible students can view open elections and candidate profiles, select candidates, review their ballot, submit it, and check their own participation status.
- Ballot submission is handled by a Django transaction. Ballot records use random IDs and do not directly reference a voter account; participation is stored separately.
- Duplicate submissions, closed elections, ineligible students, and invalid candidate/position selections are rejected by the backend.

### Administration and monitoring

- Administrators manage voter accounts, staff accounts, elections, candidate details, eligibility, and election lifecycle.
- Administrators can view aggregate participation, integrity checks, audit events, and results after an election closes. Closed-election CSV reports are available.
- Election monitors have read-only access to election status, aggregate participation, and permitted system-health information.
- Health endpoints report application/database status. A separate network-testing folder contains demonstration material; it is not part of vote submission.

See [Phase 10 notes](PHASE10-README.md), [account creation guide](docs/ACCOUNT-CREATION.md), [candidate photo guide](docs/CANDIDATE-PHOTOS.md), and [student classification/eligibility guide](docs/STUDENT-CLASSIFICATION-ELIGIBILITY.md) for feature details.

## Requirements

- Windows PowerShell (commands below) or another compatible development environment
- Python with compatible Django and MySQL client packages
- Node.js 22.12 or newer and npm
- A running local MySQL server
- Git (optional)

The backend dependencies are listed in `backend/requirements.txt`; frontend dependencies and scripts are in `frontend/package.json`.

## Local development setup

### 1. Configure the backend

Open PowerShell in the project root and run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` in a text editor. Replace the Django secret and MySQL placeholders. Generate a secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Keep `.env` private and out of Git. Use a dedicated local MySQL account, not the MySQL root account. The MySQL **server** must be running and the database named in `MYSQL_DATABASE` must exist. `mysql` command-line access is optional for Django commands; `manage.py dbshell` specifically requires the MySQL client executable to be on PATH.

The example settings are for local development. Keep MySQL bound to loopback (`127.0.0.1`) and do not expose port 3306 to student devices.

### 2. Apply migrations and check Django

Run these commands from `backend/` after configuring the local database:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py showmigrations
```

Use `.venv\Scripts\python.exe` directly if PowerShell blocks virtual-environment activation. Do not point this development project at a production database. A custom Django user model is in use; never replace its migration history or reset a database with data you need to keep.

Create the first administrator interactively:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Then assign that account the application's `ADMIN` role using the steps in [the account creation guide](docs/ACCOUNT-CREATION.md). The primary administrator is the superuser; only that account can create additional administrator accounts.

Start Django in the backend terminal:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Check `http://127.0.0.1:8000/api/health/`; a healthy response is `{"status":"ok"}`.

### 3. Start the frontend

Open a second PowerShell window in the project root:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://127.0.0.1:5173`. In PowerShell, `npm.cmd` avoids the script-execution policy error that can block `npm.ps1`. Vite proxies `/api/` and `/media/` to Django on `127.0.0.1:8000`.

To compile the static frontend:

```powershell
npm.cmd run build
```

## First-use workflow

1. Sign in as the administrator and create a Draft election.
2. Add election positions and candidates. Candidate images are optional.
3. Add student accounts with their course and year, or edit existing accounts to classify them.
4. In the election's **Positions / eligibility** setup, choose an all-student, course, or course/year group. Review the matching counts, then confirm to grant eligibility. Only active, classified students in Years 1–4 match these groups.
5. Open the election only after checking its positions, candidates, and eligible voter list.
6. Sign in as an eligible synthetic student to review and submit a development ballot. Results are available to administrators and monitors only after closure.

Deactivating a student does not delete their account or historical participation. Deactivation is blocked while they are eligible in an open election. An inactive account can be found and reactivated through **Show inactive accounts**.

## LAN development demonstration

The default setup is available only on the development computer. To open the development UI from a phone or another computer on the same authorized LAN, use this temporary workflow with **synthetic accounts and data only**. Do not send real credentials or ballots over HTTP.

### 1. Find the development computer's IPv4 address

On the computer running the project, open PowerShell and run:

```powershell
ipconfig
```

Find **IPv4 Address** under the active Wi-Fi or Ethernet adapter. The example below uses `10.67.1.123`; replace it with the current address shown on your computer. If the computer is using a phone hotspot, reconnecting may change this address.

### 2. Add that address to `backend/.env`

Open `backend/.env` in a text editor and update the development settings. `ALLOWED_HOSTS` contains host names/IP addresses only (no scheme and no port). `CSRF_TRUSTED_ORIGINS` contains the full browser origin (including `http://` and Vite's port `5173`).

```env
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,10.67.1.123
DJANGO_CSRF_TRUSTED_ORIGINS=http://10.67.1.123:5173
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
```

Keep `.env` local and uncommitted. After changing the server IP or these settings, stop and restart Django.

### 3. Start Django on loopback

In a PowerShell window, run:

```powershell
cd path\to\lan-voting-system\backend
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Keep this window open. Django stays on the development computer; Vite will proxy API and image requests to it.

### 4. Start Vite for LAN access

Open a second PowerShell window:

```powershell
cd path\to\lan-voting-system\frontend
npm.cmd run dev:lan
```

Keep this window open too. In PowerShell, `npm.cmd` avoids the execution-policy error that can block `npm.ps1`.

### 5. Open the site on the other device

Connect both devices to the same authorized Wi-Fi or hotspot. On the phone or other computer, open:

```text
http://10.67.1.123:5173
```

Replace `10.67.1.123` with the development computer's current IPv4 address. If Django logs `DisallowedHost`, check that the IP is in `DJANGO_ALLOWED_HOSTS`, then restart Django. If a state-changing request reports a CSRF origin error, check `DJANGO_CSRF_TRUSTED_ORIGINS` includes `http://<server-ip>:5173` and restart Django.

If the page does not load, confirm both terminal servers are still running and that the devices can communicate over the LAN. A firewall rule may be needed for TCP 5173 on the Private profile, scoped to the authorized LAN, if local policy permits. Do not expose ports 8000 or 3306 to student devices and do not disable the firewall or router security controls broadly.

The Vite/Django development-server arrangement is **not a production deployment**. A deployment would need a reviewed HTTPS-capable web server on a single origin, Django behind a production WSGI server bound to loopback, trusted certificates installed on client devices, scoped firewall rules, and MySQL inaccessible from student devices. Follow school IT policy; do not disable general network security to make the demo work.

## Important security and data notes

- This project has not been independently audited or certified for elections. Passing a Django check or local build does not establish election security.
- Use synthetic data while developing. Do not use live ballots over the HTTP development server.
- Ballot selections are not directly linked to user accounts in the application models, but the project has not received a formal privacy/security review. Do not claim certified ballot anonymity.
- Deactivated accounts and closed-election participation records are retained. Back up the MySQL database and the separate `backend/media/` candidate photo files.
- Uploaded candidate photos are profile images only. Do not upload identity documents or sensitive images.
- `backend/.env`, `.venv/`, `frontend/node_modules/`, build output, and media files must not be committed. Review `git status` before staging changes.

## Project layout

- `backend/` — Django settings, authentication, elections, voting, results, monitoring, and audit API
- `frontend/` — React/Vite administration, student, and monitor interfaces
- `database/` — database setup references
- `docs/` — API, account, feature, and integration guides
- `network-testing/` — separate LAN/network demonstration material

## Checks and test commands

The project includes Django checks/tests and a frontend API test script. Run these against a disposable development/test database, not production data:

```powershell
# From backend/
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test

# From frontend/
npm.cmd run test:api
```
next task to do , enhance the UI and visual for monitor
