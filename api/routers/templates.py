"""Templates router — CRUD for product templates."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.dependencies import get_db
from models.template import ProductTemplate
from models.user import User

router = APIRouter(prefix="/api/templates", tags=["templates"])


class TemplateCreate(BaseModel):
    product_type: str
    required_components: str = "[]"
    component_positions: str | None = None
    antenna_position: str | None = None
    sn_format: str | None = None
    qr_format: str | None = None


class TemplateResponse(BaseModel):
    id: int
    product_type: str
    required_components: str
    component_positions: str | None
    antenna_position: str | None
    sn_format: str | None
    qr_format: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


def _serialize(row: ProductTemplate) -> dict:
    return {
        "id": row.id,
        "product_type": row.product_type,
        "required_components": row.required_components,
        "component_positions": row.component_positions,
        "antenna_position": row.antenna_position,
        "sn_format": row.sn_format,
        "qr_format": row.qr_format,
        "created_at": str(row.created_at),
        "updated_at": str(row.updated_at),
    }


@router.post("/", response_model=TemplateResponse, status_code=201)
def create_template(
    payload: TemplateCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    existing = db.query(ProductTemplate).filter(ProductTemplate.product_type == payload.product_type).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product type already exists")

    tmpl = ProductTemplate(**payload.model_dump())
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return _serialize(tmpl)


@router.get("/", response_model=list[TemplateResponse])
def list_templates(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows = db.query(ProductTemplate).order_by(ProductTemplate.product_type).all()
    return [_serialize(r) for r in rows]


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    tmpl = db.query(ProductTemplate).filter(ProductTemplate.id == template_id).first()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return _serialize(tmpl)


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    payload: TemplateCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    tmpl = db.query(ProductTemplate).filter(ProductTemplate.id == template_id).first()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")

    for k, v in payload.model_dump().items():
        setattr(tmpl, k, v)
    db.commit()
    db.refresh(tmpl)
    return _serialize(tmpl)


@router.delete("/{template_id}", status_code=204)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    tmpl = db.query(ProductTemplate).filter(ProductTemplate.id == template_id).first()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(tmpl)
    db.commit()
