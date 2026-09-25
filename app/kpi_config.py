"""Single place naming which column of which report feeds each KPI.

The requirement doc left the exact column choice open in some cases (it
says things like "take it from column of report" without naming the
column). Entries marked BEST GUESS below should be confirmed with the
business owner before the KPI is treated as correct.
"""

# Row number where real data starts in the MTD_Theo Route sheet, everything
# above this row is the multi row header block, fixed by inspecting the file.
SALES_ROUTE_DATA_START_ROW = 8

# Column position, one based, of each field the sales report parser reads,
# fixed by inspecting the real MTD_Theo Route sheet header rows.
SALES_ROUTE_COLUMNS = {
    "area": 1,
    "route_code": 6,
    "route_name": 7,
    "route_type": 8,
    "vol_target": 37,
    "aso_coverage": 40,   # BEST GUESS, matches the glossary's ASO definition, needs confirmation
    "volume_actual": 61,  # column header is "Total Vol (Thuc Giao)", matches the PDF's Volume example directly
}

# Row number where real data starts in the SummarybyRoute sheet, everything
# above this row is the multi row header block, fixed by inspecting the file.
AI_PHOTO_ROUTE_DATA_START_ROW = 7

# Column position, one based, of each field the AI photo parser reads,
# fixed by inspecting the real SummarybyRoute sheet header rows.
AI_PHOTO_ROUTE_COLUMNS = {
    "route_code": 9,
    "route_name": 10,
    "aso_photographed": 11,  # column header is "SL ASO chup hinh", matches the PDF's AI photo example directly
}

# Exact column names used by the raw order line CSV, copied from the file
# itself since that source is a plain CSV rather than a positional sheet.
RAW_ORDERS_COLUMNS = {
    "route_code": "Mã Route",
    "route_name": "Tên Route",
    "volume_actual": " Sản lượng thực giao",
}

# Row number where real data starts in the By Route sheet, everything
# above this row is the header block, fixed by inspecting the file.
SPVB_SHOP_ROUTE_DATA_START_ROW = 8

# Column position, one based, of each field the SPVB Shop tracking parser
# reads, fixed by inspecting the real By Route sheet header rows. This file
# has no separate route name column, so the route code is reused as the label.
SPVB_SHOP_ROUTE_COLUMNS = {
    "area": 2,
    "route_code": 5,
    "aso_target": 10,     # column header is "#ASO co Chi tieu ... - sau Mien Tru", the target after exemptions
    "aso_installed": 11,  # column header is "#ASO da cai dat", ASO that already have SPVB Shop installed
}
