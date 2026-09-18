"""Serves the KPI values the frontend renders as cards and a table."""
from fastapi import APIRouter
from app.db import get_client

router = APIRouter()


@router.get("/api/dashboard")
def get_dashboard(month: str):
    # Returns every KPI value stored for the requested month, one object per route.
    client = get_client()
    result = client.execute(
        "SELECT kpi_name, scope_key, scope_label, value, source_report "
        "FROM kpi_snapshots WHERE report_month = ? AND source_report != 'raw_orders'",
        [month],
    )
    client.close()
    routes = {}
    for kpi_name, scope_key, scope_label, value, source_report in result.rows:
        route = routes.setdefault(scope_key, {"route_code": scope_key, "route_name": scope_label})
        route[kpi_name] = value
    return {"month": month, "routes": list(routes.values())}


@router.get("/api/months")
def get_months():
    # Returns the distinct months that have data, used to fill the month dropdown.
    client = get_client()
    result = client.execute(
        "SELECT DISTINCT report_month FROM kpi_snapshots ORDER BY report_month DESC"
    )
    client.close()
    return {"months": [row[0] for row in result.rows]}
