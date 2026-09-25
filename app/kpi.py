"""Turns parsed report rows into kpi_snapshots rows and writes them to the database."""
from datetime import datetime, timezone
from app.db import upsert_kpi_snapshot


def _now():
    # Timestamp stamped on every KPI row, so it is clear when it was computed.
    return datetime.now(timezone.utc).isoformat()


def write_sales_route_kpis(client, report_month, rows):
    # Stores Vol Target, Volume Actual and ASO Coverage for every route
    # found in the sales report.
    now = _now()
    for r in rows:
        for kpi_name, value in [
            ("vol_target", r["vol_target"]),
            ("volume_actual", r["volume_actual"]),
            ("aso_coverage", r["aso_coverage"]),
        ]:
            upsert_kpi_snapshot(
                client, report_month, kpi_name, "route", r["route_code"],
                r["route_name"], value, "sales_report", now,
            )


def write_ai_photo_route_kpis(client, report_month, rows):
    # Stores the count of ASO that were photographed, per route.
    now = _now()
    for r in rows:
        upsert_kpi_snapshot(
            client, report_month, "aso_photographed", "route", r["route_code"],
            r["route_name"], r["aso_photographed"], "ai_photo_report", now,
        )


def write_raw_orders_volume_kpi(client, report_month, rows):
    # Stores Volume Actual computed straight from the raw order lines,
    # under its own source_report so it can be compared against the sales
    # report figure instead of silently overwriting it.
    now = _now()
    for r in rows:
        upsert_kpi_snapshot(
            client, report_month, "volume_actual", "route", r["route_code"],
            r["route_name"], r["volume_actual"], "raw_orders", now,
        )


def write_spvb_shop_route_kpis(client, report_month, rows):
    # Stores the SPVB Shop install target and install count for every
    # route. The route code is reused as the label since this source has
    # no separate route name column.
    now = _now()
    for r in rows:
        for kpi_name, value in [
            ("spvb_shop_target", r["aso_target"]),
            ("spvb_shop_installed", r["aso_installed"]),
        ]:
            upsert_kpi_snapshot(
                client, report_month, kpi_name, "route", r["route_code"],
                r["route_code"], value, "spvb_shop_tracking", now,
            )


def recompute_aso_not_photographed(client, report_month):
    # Derives ASO not yet photographed per route by subtracting
    # aso_photographed from aso_coverage for the same route and month, the
    # cross report KPI named as an example in the requirement doc.
    coverage_result = client.execute(
        "SELECT scope_key, scope_label, value FROM kpi_snapshots "
        "WHERE report_month = ? AND kpi_name = 'aso_coverage'",
        [report_month],
    )
    photographed_result = client.execute(
        "SELECT scope_key, value FROM kpi_snapshots "
        "WHERE report_month = ? AND kpi_name = 'aso_photographed'",
        [report_month],
    )
    photographed_by_route = {row[0]: row[1] for row in photographed_result.rows}
    now = _now()
    for scope_key, scope_label, coverage in coverage_result.rows:
        photographed = photographed_by_route.get(scope_key, 0)
        upsert_kpi_snapshot(
            client, report_month, "aso_not_photographed", "route", scope_key,
            scope_label, (coverage or 0) - (photographed or 0), "derived", now,
        )
