# Local account creation

Use synthetic accounts for development. Share temporary passwords with account holders privately.

## First administrator

Create the primary administrator from `backend/` with Django's normal prompt:

```powershell
python manage.py createsuperuser
```

Then assign the application role to that superuser:

```powershell
python manage.py shell
```

At the Python prompt:

```python
from accounts.models import User
user = User.objects.get(username='YOUR_USERNAME')
user.role = User.Role.ADMIN
user.save(update_fields=['role'])
```

The account remains a Django superuser and is treated as the primary administrator. Only this account can create additional `ADMIN` accounts in the staff page.

## Student accounts

An `ADMIN` creates students in **Voter Management → Add Student** with a student ID and temporary password. The API marks the new account as requiring a password change. The first sign-in can only reach the password-change page until the temporary password is replaced.

## Monitor and additional administrator accounts

An `ADMIN` creates `MONITOR` accounts in **Staff Accounts**. Only the primary administrator can select the `ADMIN` role. Staff accounts receive a temporary password and must change it at first sign-in.

The initial password is validated by Django's configured password validators, stored as a password hash, and never returned from the API. Existing accounts are not forced to change their password by the new field's default.
