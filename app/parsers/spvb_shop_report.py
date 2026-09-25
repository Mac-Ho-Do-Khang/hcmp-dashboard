"""Extracts route level KPI values from the SPVB Shop tracking workbook.

This source is a xlsb binary workbook rather than xlsx, so it is read
with pyxlsb instead of openpyxl.
"""
from pyxlsb import open_workbook
from app.kpi_config import SPVB_SHOP_ROUTE_COLUMNS, SPVB_SHOP_ROUTE_DATA_START_ROW

# Name of the sheet inside the workbook that holds route level install counts.
SHEET_NAME = "By Route"


def _cell_value(row, column):
    # Reads one cell by its one based column position, treating a row that
    # ends early because its trailing cells were blank as if those cells
    # were present and empty, instead of raising an index error.
    index = column - 1
    if index < len(row):
        return row[index].v
    return None


def parse_spvb_shop_route_kpis(file_path):
    # Reads every route row and returns one dict per route with the SPVB
    # Shop install target and install count, stopping at the first blank route code.
    with open_workbook(file_path) as wb:
        if SHEET_NAME not in wb.sheets:
            # Wrong report type picked for this file is the most likely
            # cause, so the message names both the sheet expected and
            # the sheets actually present.
            raise ValueError(
                "Sheet '" + SHEET_NAME + "' not found, is this the right report type for this file? "
                "Sheets in file: " + ", ".join(wb.sheets)
            )
        cols = SPVB_SHOP_ROUTE_COLUMNS
        results = []
        with wb.get_sheet(SHEET_NAME) as sheet:
            for row_number, row in enumerate(sheet.rows(), start=1):
                if row_number < SPVB_SHOP_ROUTE_DATA_START_ROW:
                    continue
                route_code = _cell_value(row, cols["route_code"])
                if not route_code:
                    break
                results.append({
                    "area": _cell_value(row, cols["area"]),
                    "route_code": str(route_code),
                    "aso_target": _cell_value(row, cols["aso_target"]) or 0,
                    "aso_installed": _cell_value(row, cols["aso_installed"]) or 0,
                })
        return results
