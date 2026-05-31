import os
import time

from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from api.websocket_manager import alert_manager

load_dotenv()

app = FastAPI(
    title="Quality Control System",
    description="Hệ thống kiểm tra chất lượng sản phẩm bằng Computer Vision",
    version="1.0.0",
)

# CORS — restrict to configured origins in production
_allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Security Headers Middleware ───────────────────────────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# ── Request Logging Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    if duration > 2 or response.status_code >= 400:
        print(f"[{request.method}] {request.url.path} -> {response.status_code} ({duration:.2f}s)")
    return response


# ── API Routers (registered FIRST — highest priority) ─────────────────────────
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


# ── Health & WebSocket (explicit paths — before catch-all) ───────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/alerts")
async def websocket_alerts(ws: WebSocket):
    """WebSocket endpoint cho real-time alert notifications."""
    await alert_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        await alert_manager.disconnect(ws)
    except Exception:
        await alert_manager.disconnect(ws)


@app.get("/ws/status")
async def websocket_status():
    return {
        "active_connections": alert_manager.connection_count,
        "status": "ok",
    }


# ── Frontend Static Files (LAST — catch-all after all API routes) ────────────
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="static-assets")

    @app.get("/")
    async def root():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Catch-all: serve frontend files or fallback to index.html for SPA routing."""
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "name": "Quality Control System",
            "version": "1.0.0",
            "status": "running",
        }
