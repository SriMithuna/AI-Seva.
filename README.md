# AI Seva

AI Seva is a Django citizen portal for browsing government schemes and services, preparing guidance requests, and tracking those requests.

## Project layout

```text
aiseva/                 Django project settings, root URLs, ASGI and WSGI
portal/                 Shared portal models, views, templates, static assets and commands
departments/            Department-specific catalogs, views, forms, templates and workflows
  agriculture/
  education/
  health/
  housing_rural/
  labour_msme/
  law_justice/
  postal/
  tamil_nadu/
reference/               Standalone visual reference page; not part of Django routing
scripts/one_off/         Historical source-repair scripts; not part of the running site
media/                   Local uploaded files
staticfiles/             Generated output from collectstatic
db.sqlite3               Local development database
manage.py                Django management entry point
requirements.txt         Python dependencies
build.sh                 Deployment build steps
```

Keep reusable department behavior in that department's app. Shared behavior belongs in `portal/`; project-wide routing and settings belong in `aiseva/`. Django templates and static assets should stay beside their owning app.

## Local setup

From the project root in PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py load_schemes
python manage.py runserver
```

Edit `.env` with local credentials as needed. Do not commit `.env`, the local database, uploaded media, or collected static output.

## Scheme catalog

`python manage.py load_schemes` loads or updates the shared scheme catalog from the department seed data and management command. Run it after changing catalog seed definitions.

The scripts under `scripts/one_off/` are old, targeted repairs rather than routine setup commands. Read [scripts/one_off/README.md](scripts/one_off/README.md) before running one.
