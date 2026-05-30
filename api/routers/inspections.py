"""Inspections router — CRUD + stats."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.dependencies import get_db
from models.user import User
from services import inspection_service

router = APIRouter(prefix="/api/inspections", tags=["inspections"])


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class InspectionCreate(BaseModel):
    product_serial: str
    product_type: str
    batch_number: str | None = None
    station_id: str
    overall_result: str = "pending"
    missing_components: str | None = None
    qr_result: str | None = None
    sn_result: str | None = None
    antenna_result: str | None = None
    image_path: str | None = None
    inference_time_ms: float | None = None


class InspectionResponse(BaseModel):
    id: int
    product_serial: str
    product_type: str
    batch_number: str | None
    station_id: str
    overall_result: str
    missing_components: str | None
    qr_result: str | None
    sn_result: str | None
    antenna_result: str | None
    image_path: str | None
    inference_time_ms: float | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class InspectionStats(BaseModel):
    total: int
    passed: int
    failed: int
    pass_rate: float
    pending: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/", response_model=InspectionResponse, status_code=201)
def create_inspection(
    payload: InspectionCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    insp = inspection_service.create_inspection(db, payload.model_dump())
    return _serialize(insp)


@router.get("/", response_model=list[InspectionResponse])
def list_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    station_id: str | None = None,
    product_type: str | None = None,
    overall_result: str | None = None,
    batch_number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows = inspection_service.list_inspections(
        db,
        skip=skip,
        limit=limit,
        station_id=station_id,
        product_type=product_type,
        overall_result=overall_result,
        batch_number=batch_number,
        start_date=start_date,
        end_date=end_date,
    )
    return [_serialize(r) for r in rows]


@router.get("/stats", response_model=InspectionStats)
def get_stats(
    station_id: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return inspection_service.get_inspection_stats(db, station_id)


@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    insp = inspection_service.get_inspection(db, inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return _serialize(insp)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serialize(row) -> dict:
    """Convert ORM row to dict with string dates."""
    return {
        "id": row.id,
        "product_serial": row.product_serial,
        "product_type": row.product_type,
        "batch_number": row.batch_number,
        "station_id": row.station_id,
        "overall_result": row.overall_result,
        "missing_components": row.missing_components,
        "qr_result": row.qr_result,
        "sn_result": row.sn_result,
        "antenna_result": row.antenna_result,
        "image_path": row.image_path,
        "inference_time_ms": row.inference_time_ms,
        "created_at": str(row.created_at),
        "updated_at": str(row.updated_at),
    }
