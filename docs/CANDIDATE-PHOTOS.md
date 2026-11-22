# Candidate profile photos

Candidate photos are optional profile images. The API accepts JPG/JPEG, PNG, and WebP files up to 2 MB, validates the decoded image format and dimensions, and stores them under random names in `backend/media/candidates/`. The database stores the media-relative path. Existing candidates without an image continue to show initials.

Install the backend dependency from `backend/requirements.txt`, then apply the new migration from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
```

For local `runserver` development, set `DJANGO_DEBUG=True` in `backend/.env`. Django serves media during development and Vite proxies `/media/` to Django. The development media route is not enabled when `DEBUG` is false. A production deployment must serve `/media/` through its configured web server over HTTPS and preserve access controls appropriate for the election.

Do not upload sensitive identity documents. The feature is for displaying profile photos only; it does not perform facial recognition or identity verification. Uploaded image files live outside the database and need their own backup plan.
