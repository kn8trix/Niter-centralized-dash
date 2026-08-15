# Niter-centralized-dash

## Demo Accounts

`db.sqlite3` is gitignored, so a fresh clone starts with **no users**. Create the
documented demo accounts with:

```bash
venv/bin/python manage.py seed_demo_users
```

| Username | Password | Role | Access |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | Superuser + staff | Every dashboard — `/admin-dashboard/`, `/medical/admin/`, `/host/medical/`, `/cafeteria/admin/`, `/clubs/manage/`, Django `/admin/`, Website Builder |
| `student` | `student123` | Regular student | Student pages — `/dashboard/`, `/tickets/`, `/meals/`, `/transport/`, `/medical/`, `/notes/`, `/study-corner/`, `/research-ai/` |

Options: `--password 'S3cret!x'` overrides the admin password;
`--extra-staff N` also creates `staff1..staffN` admin accounts. The command is
idempotent — existing users are never touched or reset.