"""Export business logic — Excel, CSV, SQL dump."""

import csv
import io
import os
from datetime import date

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import settings
from models.inspection import Inspection

EXPORT_DIR = settings.EXPORT_DIR
os.makedirs(EXPORT_DIR, exist_ok=True)


def _query_inspections(
    db: Session,
    station_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Inspection]:
    q = db.query(Inspection)
    if station_id:
        q = q.filter(Inspection.station_id == station_id)
    if start_date:
        q = q.filter(Inspection.created_at >= str(start_date))
    if end_date:
        q = q.filter(Inspection.created_at <= str(end_date))
    return q.order_by(Inspection.created_at.desc()).all()


def _to_dataframe(rows: list[Inspection]) -> pd.DataFrame:
    records = []
    for r in rows:
        records.append(
            {
                "ID": r.id,
                "Serial": r.product_serial,
                "Product Type": r.product_type,
                "Batch": r.batch_number,
                "Station": r.station_id,
                "Result": r.overall_result,
                "QR": r.qr_result,
                "SN": r.sn_result,
                "Antenna": r.antenna_result,
                "Missing Components": r.missing_components,
                "Inference (ms)": r.inference_time_ms,
                "Created At": str(r.created_at),
            }
        )
    return pd.DataFrame(records)


def export_excel(
    db: Session,
    station_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> str:
    """Export inspections to .xlsx and return the file path."""
    rows = _query_inspections(db, station_id, start_date, end_date)
    df = _to_dataframe(rows)
    filename = f"inspections_{date.today().isoformat()}.xlsx"
    filepath = os.path.join(EXPORT_DIR, filename)
    df.to_excel(filepath, index=False, engine="openpyxl")
    return filepath


def export_csv(
    db: Session,
    station_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> str:
    """Export inspections to .csv and return the file path."""
    rows = _query_inspections(db, station_id, start_date, end_date)
    df = _to_dataframe(rows)
    filename = f"inspections_{date.today().isoformat()}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)
    df.to_csv(filepath, index=False)
    return filepath


def export_sql(
    db: Session,
    station_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> str:
    """Export inspections as SQL INSERT statements."""
    rows = _query_inspections(db, station_id, start_date, end_date)
    filename = f"inspections_{date.today().isoformat()}.sql"
    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, "w") as f:
        for r in rows:
            f.write(
                f"INSERT INTO inspections (id, product_serial, product_type, batch_number, "
                f"station_id, overall_result, missing_components, qr_result, sn_result, "
                f"antenna_result, image_path, inference_time_ms, created_at, updated_at) "
                f"VALUES ({r.id}, '{r.product_serial}', '{r.product_type}', "
                f"'{r.batch_number}', '{r.station_id}', '{r.overall_result}', "
                f"'{r.missing_components}', '{r.qr_result}', '{r.sn_result}', "
                f"'{r.antenna_result}', '{r.image_path}', {r.inference_time_ms or 'NULL'}, "
                f"'{r.created_at}', '{r.updated_at}');\n"
            )
    return filepath
