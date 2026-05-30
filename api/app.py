import os
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
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
    # Chặn clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    # Chặn MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Strict Transport Security (HTTPS)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Permissions Policy
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# ── Request Logging Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    # Chỉ log các request chậm (>2s) hoặc lỗi
    if duration > 2 or response.status_code >= 400:
        print(f"[{request.method}] {request.url.path} -> {response.status_code} ({duration:.2f}s)")
    return response

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


# ── WebSocket — Real-time alerts ─────────────────────────────────────────────
@app.websocket("/ws/alerts")
async def websocket_alerts(ws: WebSocket):
    """WebSocket endpoint cho real-time alert notifications.
    
    Client kết nối: ws://host:port/ws/alerts
    Nhận JSON messages khi có sản phẩm lỗi.
    """
    await alert_manager.connect(ws)
    try:
        while True:
            # Giữ connection alive, chờ data từ client (ping/pong)
            data = await ws.receive_text()
            # Client có thể gửi "ping", server trả "pong"
            if data == "ping":
                await ws.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        await alert_manager.disconnect(ws)
    except Exception:
        await alert_manager.disconnect(ws)


@app.get("/ws/status")
async def websocket_status():
    """Kiểm tra trạng thái WebSocket connections."""
    return {
        "active_connections": alert_manager.connection_count,
        "status": "ok",
    }
