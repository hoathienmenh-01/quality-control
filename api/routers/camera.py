"""Camera router — capture, status, connect."""

import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.dependencies import get_db
from models.user import User

router = APIRouter(prefix="/api/camera", tags=["camera"])

# In-memory camera state (production would use Redis or DB)
_camera_state: dict = {
    "connected": False,
    "camera_id": int(os.getenv("CAMERA_ID", "0")),
    "resolution": (
        int(os.getenv("CAMERA_RESOLUTION_WIDTH", "1920")),
        int(os.getenv("CAMERA_RESOLUTION_HEIGHT", "1080")),
    ),
    "last_capture": None,
}


class CameraStatus(BaseModel):
    connected: bool
    camera_id: int
    resolution: tuple[int, int]
    last_capture: str | None


class CaptureResponse(BaseModel):
    success: bool
    image_path: str | None
    message: str


@router.get("/status", response_model=CameraStatus)
def camera_status(_user: User = Depends(get_current_user)):
    return CameraStatus(**_camera_state)


@router.post("/connect", response_model=CameraStatus)
def camera_connect(_user: User = Depends(get_current_user)):
    """Connect to the camera (stub — real impl in core/camera.py)."""
    _camera_state["connected"] = True
    return CameraStatus(**_camera_state)


@router.post("/disconnect", response_model=CameraStatus)
def camera_disconnect(_user: User = Depends(get_current_user)):
    _camera_state["connected"] = False
    return CameraStatus(**_camera_state)


@router.post("/capture", response_model=CaptureResponse)
def capture_image(_user: User = Depends(get_current_user)):
    """Capture a single frame (stub)."""
    if not _camera_state["connected"]:
        raise HTTPException(status_code=400, detail="Camera not connected")

    # Stub: in production, call core/camera.py to grab a frame
    from datetime import datetime

    captures_dir = os.getenv("CAPTURE_DIR", "./captures")
    os.makedirs(captures_dir, exist_ok=True)
    filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(captures_dir, filename)

    # Placeholder — real implementation grabs from OpenCV
    _camera_state["last_capture"] = datetime.now().isoformat()

    return CaptureResponse(
        success=True,
        image_path=filepath,
        message="Capture successful (stub — connect real camera core)",
    )
