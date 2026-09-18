"""Aggregates the raw order line CSV into per route delivered volume.

Kept separate from sales_report.py to demonstrate that the same KPI
(volume_actual) can be produced from more than one data source, stored
under a different source_report value rather than overwriting each other.
"""
import unicodedata
import pandas as pd
from app.kpi_config import RAW_ORDERS_COLUMNS


def _normalize(text):
    # Converts Vietnamese text to precomposed Unicode form, since some
    # exports store accented letters as a base letter plus a separate
    # combining mark, which would otherwise fail to match by name.
    return unicodedata.normalize("NFC", text)


def parse_raw_orders_volume(file_path):
    # Sums delivered volume per route straight from the raw order line export.
    cols = RAW_ORDERS_COLUMNS
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df.columns = [_normalize(c) for c in df.columns]
    df = df[[cols["route_code"], cols["route_name"], cols["volume_actual"]]]
    grouped = (
        df.groupby([cols["route_code"], cols["route_name"]])[cols["volume_actual"]]
        .sum()
        .reset_index()
    )
    return [
        {
            "route_code": str(row[cols["route_code"]]),
            "route_name": row[cols["route_name"]],
            "volume_actual": row[cols["volume_actual"]],
        }
        for _, row in grouped.iterrows()
    ]
