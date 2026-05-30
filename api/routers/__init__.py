from api.routers.alerts import router as alerts_router
from api.routers.auth import router as auth_router
from api.routers.camera import router as camera_router
from api.routers.dashboard import router as dashboard_router
from api.routers.defects import router as defects_router
from api.routers.export import router as export_router
from api.routers.inspections import router as inspections_router
from api.routers.templates import router as templates_router

__all__ = [
    "alerts_router",
    "auth_router",
    "camera_router",
    "dashboard_router",
    "defects_router",
    "export_router",
    "inspections_router",
    "templates_router",
]
