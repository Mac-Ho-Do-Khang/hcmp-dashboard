"""Extracts route level KPI values from the MTD Sales Daily Report workbook."""
import openpyxl
from app.kpi_config import SALES_ROUTE_COLUMNS, SALES_ROUTE_DATA_START_ROW

# Name of the sheet inside the workbook that holds route level MTD figures.
SHEET_NAME = "MTD_Theo Route"


def parse_sales_route_kpis(file_path):
    # Reads every route row and returns one dict per route with the KPI
    # values this app currently tracks, stopping at the first blank route code.
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb[SHEET_NAME]
    cols = SALES_ROUTE_COLUMNS
    results = []
    for row in ws.iter_rows(min_row=SALES_ROUTE_DATA_START_ROW, values_only=True):
        route_code = row[cols["route_code"] - 1]
        if not route_code:
            break
        results.append({
            "area": row[cols["area"] - 1],
            "route_code": str(route_code),
            "route_name": row[cols["route_name"] - 1],
            "route_type": row[cols["route_type"] - 1],
            "vol_target": row[cols["vol_target"] - 1] or 0,
            "volume_actual": row[cols["volume_actual"] - 1] or 0,
            "aso_coverage": row[cols["aso_coverage"] - 1] or 0,
        })
    wb.close()
    return results
