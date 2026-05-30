from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Quality Control System",
    description="Hệ thống kiểm tra chất lượng sản phẩm bằng Computer Vision",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from api.routers import (
    alerts_router,
    auth_router,
    camera_router,
    dashboard_router,
    defects_router,
    export_router,
    inspections_router,
    templates_router,
)

app.include_router(auth_router)
app.include_router(inspections_router)
app.include_router(templates_router)
app.include_router(export_router)
app.include_router(defects_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(camera_router)


# ── Health endpoints ──────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "Quality Control System",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
