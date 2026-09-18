"""Database access for the dashboard.

Wraps the libsql client so the rest of the app never deals with connection
details directly, and works the same way against a local file during
development and against Turso in production.
"""
import os
import libsql_client

# File used when no Turso credentials are set, so the app runs fully
# offline during development without needing a Turso account.
LOCAL_DB_PATH = "file:local.db"

# SQL that creates every table the app relies on, run once at startup.
SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS kpi_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_month TEXT NOT NULL,
        kpi_name TEXT NOT NULL,
        scope_type TEXT NOT NULL,
        scope_key TEXT NOT NULL,
        scope_label TEXT,
        value REAL,
        source_report TEXT NOT NULL,
        uploaded_at TEXT NOT NULL,
        UNIQUE(report_month, kpi_name, scope_type, scope_key, source_report)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_type TEXT NOT NULL,
        filename TEXT NOT NULL,
        report_month TEXT NOT NULL,
        row_count INTEGER NOT NULL,
        uploaded_at TEXT NOT NULL
    )
    """,
]


def _to_http_url(url):
    # Turso gives out database URLs starting with libsql, which this
    # client only connects to over websocket, and that handshake can be
    # blocked on some hosts. Rewriting to https keeps the same database
    # but uses the plain HTTP transport instead, which is more portable.
    if url.startswith("libsql://"):
        return "https://" + url[len("libsql://"):]
    return url


def get_client():
    # Builds a libsql client, pointed at Turso when its env vars are set
    # and at a local file otherwise, so the same code path works in both
    # development and production.
    url = os.environ.get("TURSO_DB_URL") or LOCAL_DB_PATH
    token = os.environ.get("TURSO_AUTH_TOKEN") or None
    if token:
        return libsql_client.create_client_sync(url=_to_http_url(url), auth_token=token)
    return libsql_client.create_client_sync(url=url)


def init_db():
    # Creates every table if it does not exist yet, safe to call on every startup.
    client = get_client()
    for statement in SCHEMA_STATEMENTS:
        client.execute(statement)
    client.close()


def upsert_kpi_snapshot(client, report_month, kpi_name, scope_type, scope_key,
                         scope_label, value, source_report, uploaded_at):
    # Writes one KPI value, replacing any existing value for the same
    # month, KPI, scope and source instead of creating a duplicate row.
    client.execute(
        """
        INSERT INTO kpi_snapshots
            (report_month, kpi_name, scope_type, scope_key, scope_label, value, source_report, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(report_month, kpi_name, scope_type, scope_key, source_report)
        DO UPDATE SET value=excluded.value, scope_label=excluded.scope_label, uploaded_at=excluded.uploaded_at
        """,
        [report_month, kpi_name, scope_type, scope_key, scope_label, value, source_report, uploaded_at],
    )


def log_upload(client, report_type, filename, report_month, row_count, uploaded_at):
    # Records one upload event, so the admin page can show a short history.
    client.execute(
        """
        INSERT INTO uploads (report_type, filename, report_month, row_count, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        [report_type, filename, report_month, row_count, uploaded_at],
    )
