# HCMP Dashboard

A small FastAPI app that stores KPI values parsed from the daily sales report, the AI photo check report, the raw order line export, and the SPVB Shop install tracking workbook, and shows them as a web dashboard. One process serves both the API and the static frontend.

## How it works

- `POST /upload` takes a report file, a report type, and a target month, parses the file, and writes KPI rows to the database. It requires an `X-Admin-Token` header.
- `GET /api/dashboard?month=YYYYMM` returns every KPI value stored for that month, one object per route.
- `GET /api/months` returns the list of months that already have data, used to fill the month dropdown.
- The database is SQLite, accessed through the libsql client, which works against a local file during development and against a hosted Turso database in production without any code changes.
- Which column of which report feeds each KPI is defined in `app/kpi_config.py`. Some entries there are marked as best guesses because the original requirement document did not name the exact column to use. Confirm those before trusting the numbers in production, in particular the `aso_coverage` mapping.

## Project layout

```
app/
  main.py              entry point, wires routers and serves static files
  db.py                database connection, schema, upsert helpers
  auth.py              admin token check used by the upload endpoint
  kpi.py               turns parsed rows into KPI rows and writes them
  kpi_config.py         which column of which report feeds each KPI
  parsers/              one file per report type, turns a file into rows
  routers/               the two API endpoints
static/                  the frontend, plain HTML, CSS and JS, no build step
```

## Local setup

Requires Python 3.11 or newer.

1. Create and activate a virtual environment.

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies.

   ```
   pip install -r requirements.txt
   ```

3. Copy the environment file and set an admin token.

   ```
   copy .env.example .env
   ```

   Open `.env` and set `ADMIN_TOKEN` to any value, this is the password the upload page will ask for. Leave `TURSO_DB_URL` and `TURSO_AUTH_TOKEN` empty for now, the app will create a local file `local.db` automatically.

4. Run the app.

   ```
   uvicorn app.main:app --reload
   ```

5. Open `http://127.0.0.1:8000/` for the dashboard, and `http://127.0.0.1:8000/admin.html` to upload a report. The admin token asked on that page is the `ADMIN_TOKEN` value from `.env`.

## Setting up Turso for production

Turso keeps the SQLite database persisted between deploys, which a free hosting tier usually does not do on its own disk.

1. Create a free account at turso.tech and install their CLI, or use their web dashboard.
2. Create a database, for example named `hcmp-dashboard`.
3. Get the database URL, it looks like `libsql://hcmp-dashboard-yourname.turso.io`.
4. Create an auth token for that database.
5. Set `TURSO_DB_URL` and `TURSO_AUTH_TOKEN` to those two values, either in your local `.env` file or in your hosting provider's environment variable settings. Keep the URL in the `libsql://` form Turso gives you, `app/db.py` rewrites it to `https://` internally before connecting, so the traffic goes over plain HTTP instead of a websocket upgrade, which some hosts block or reset.

No other code change is needed, `app/db.py` switches to Turso automatically once those two variables are set.

## Deploying to Render

1. Push this project to a GitHub repository.
2. On render.com, create a new Web Service and connect that repository.
3. Set the build command to `pip install -r requirements.txt`.
4. Set the start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. In the service's environment variables, set `ADMIN_TOKEN`, `TURSO_DB_URL` and `TURSO_AUTH_TOKEN` to the same values used locally.
6. Deploy. Render gives you a public URL such as `https://hcmp-dashboard.onrender.com`.

The free tier spins the service down after about fifteen minutes without traffic, so the first request after a quiet period takes thirty to fifty seconds to respond while it wakes up. For a dashboard checked a few times a day this is a minor inconvenience rather than a problem. If it becomes annoying, moving to Railway's always on hobby plan needs the same three steps above, just on a different host.

## Uploading a report

On the admin page, pick the report type, type the month as `YYYYMM`, for example `202608`, choose the file, enter the admin token, and submit. The report types currently supported are:

- Sales Daily Report, reading the `MTD_Theo Route` sheet.
- AI Photo Report, reading the `SummarybyRoute` sheet.
- The raw order line CSV export.
- SPVB Shop Tracking, reading the `By Route` sheet of the xlsb workbook. This one is a xlsb binary file rather than xlsx, read with the pyxlsb library instead of openpyxl. This source has no separate route name column, so the route code is shown as its own label in the table.

Re-uploading a report for a month that already has data replaces the previous values for that month and source rather than duplicating them.

## Known gaps

- Only seven KPIs are wired up so far, volume target, volume actual, ASO coverage, ASO photographed, the derived ASO not photographed, SPVB Shop target, and SPVB Shop installed. Adding another KPI means adding its column position to `app/kpi_config.py`, reading it in the matching parser, and writing it in `app/kpi.py`.
- The `aso_coverage` column mapping is a best guess and needs confirmation, see the comment in `app/kpi_config.py`.
- There is no way yet to browse or correct a bad upload from the admin page besides re-uploading the file.
