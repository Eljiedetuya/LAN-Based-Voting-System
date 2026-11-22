# Student course and year classification

Student accounts can be classified as BSIT or BIT and Year 1 through Year 4. New accounts require both values; older student accounts remain valid but are not included in bulk eligibility until an administrator classifies them.

In election setup, an administrator selects a student group from the **Eligible voters** dropdown. The matching count appears before the administrator confirms the assignment. The server processes every active classified student in the selected group, regardless of the voter list's current page, and adds them to the eligible voter list. Repeating an assignment is safe because election/user eligibility is unique. The endpoint only creates eligibility records and does not change ballots. Both preview and assignment are restricted to Draft elections on the server.

To add the fields to an existing database, run from `backend/`:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

Existing accounts can be classified from **Administration → Voters → Edit**. New accounts can optionally be granted eligibility for one selected Draft election; leaving that field empty creates the account without election eligibility.
