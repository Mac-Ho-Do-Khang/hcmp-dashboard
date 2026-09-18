"""Receives an uploaded report file, parses it, and writes its KPIs to the database."""
import os
import shutil
import tempfile
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse

from app.auth import require_admin
from app.db import get_client, log_upload
from app.parsers.sales_report import parse_sales_route_kpis
from app.parsers.ai_photo_report import parse_ai_photo_route_kpis
from app.parsers.raw_orders import parse_raw_orders_volume
from app.kpi import (
    write_sales_route_kpis,
    write_ai_photo_route_kpis,
    write_raw_orders_volume_kpi,
    recompute_aso_not_photographed,
)

router = APIRouter()

# Maps the report type selected in the upload form to its parser and its
# KPI writer, the one place that needs a new entry when a report type is added.
REPORT_HANDLERS = {
    "sales_report": (parse_sales_route_kpis, write_sales_route_kpis),
    "ai_photo_report": (parse_ai_photo_route_kpis, write_ai_photo_route_kpis),
    "raw_orders": (parse_raw_orders_volume, write_raw_orders_volume_kpi),
}


@router.post("/upload")
def upload_report(
    report_type: str = Form(...),
    report_month: str = Form(...),
    file: UploadFile = File(...),
    _admin=Depends(require_admin),
):
    # Saves the upload to a temp file, parses it, writes the KPI rows, and
    # recomputes the KPI that depends on more than one report.
    if report_type not in REPORT_HANDLERS:
        return {"error": "Unknown report_type: " + report_type}

    parse_fn, write_fn = REPORT_HANDLERS[report_type]
    suffix = os.path.splitext(file.filename)[1]
    # The upload may have already been read once while the multipart body
    # was parsed, so the position must be reset to the start before copying.
    file.file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        try:
            rows = parse_fn(tmp_path)
            client = get_client()
            try:
                write_fn(client, report_month, rows)
                recompute_aso_not_photographed(client, report_month)
                log_upload(
                    client, report_type, file.filename, report_month,
                    len(rows), datetime.now(timezone.utc).isoformat(),
                )
            finally:
                client.close()
        finally:
            # Best effort cleanup, ignored if the file is still briefly
            # locked, so a cleanup failure never hides the real error above.
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    except Exception as e:
        # Turns a parsing or database failure into a readable JSON error
        # instead of a bare 500, most often caused by the selected report
        # type not matching the uploaded file.
        return JSONResponse(status_code=400, content={"error": str(e)})

    return {"status": "ok", "rows_processed": len(rows)}
