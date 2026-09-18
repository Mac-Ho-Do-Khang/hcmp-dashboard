"""Extracts route level KPI values from the AI photo check workbook."""
import openpyxl
from app.kpi_config import AI_PHOTO_ROUTE_COLUMNS, AI_PHOTO_ROUTE_DATA_START_ROW

# Name of the sheet inside the workbook that holds route level photo counts.
SHEET_NAME = "SummarybyRoute"


def parse_ai_photo_route_kpis(file_path):
    # Reads every route row and returns one dict per route with the count
    # of ASO that were photographed, stopping at the first blank route code.
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    try:
        if SHEET_NAME not in wb.sheetnames:
            # Wrong report type picked for this file is the most likely
            # cause, so the message names both the sheet expected and
            # the sheets actually present.
            raise ValueError(
                "Sheet '" + SHEET_NAME + "' not found, is this the right report type for this file? "
                "Sheets in file: " + ", ".join(wb.sheetnames)
            )
        ws = wb[SHEET_NAME]
        cols = AI_PHOTO_ROUTE_COLUMNS
        results = []
        for row in ws.iter_rows(min_row=AI_PHOTO_ROUTE_DATA_START_ROW, values_only=True):
            route_code = row[cols["route_code"] - 1]
            if not route_code:
                break
            results.append({
                "route_code": str(route_code),
                "route_name": row[cols["route_name"] - 1],
                "aso_photographed": row[cols["aso_photographed"] - 1] or 0,
            })
        return results
    finally:
        # Closed even when a sheet is missing or a row fails to parse, so
        # the caller can always delete the temp file right after this returns.
        wb.close()
