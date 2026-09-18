"""Extracts route level KPI values from the AI photo check workbook."""
import openpyxl
from app.kpi_config import AI_PHOTO_ROUTE_COLUMNS, AI_PHOTO_ROUTE_DATA_START_ROW

# Name of the sheet inside the workbook that holds route level photo counts.
SHEET_NAME = "SummarybyRoute"


def parse_ai_photo_route_kpis(file_path):
    # Reads every route row and returns one dict per route with the count
    # of ASO that were photographed, stopping at the first blank route code.
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
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
    wb.close()
    return results
