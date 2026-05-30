"""Notification Service — Tự động cảnh báo khi sản phẩm lỗi.

Tính năng:
- Tạo Alert record khi inspection FAIL
- Gửi thông báo Telegram real-time
- Broadcast WebSocket real-time đến frontend
- Theo dõi lỗi liên tiếp per station (consecutive fail threshold)
- Theo dõi tỷ lệ lỗi (fail rate threshold)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta

import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session

from config import settings
from models.alert import Alert
from models.inspection import Inspection

logger = logging.getLogger(__name__)

# ── In-memory state for consecutive failures ─────────────────────────────────
# Key: station_id, Value: consecutive fail count
# Reset on restart or when inspection passes
_consecutive_fails: dict[str, int] = {}


def get_consecutive_fails(station_id: str) -> int:
    """Đếm số lần lỗi liên tiếp tại station."""
    return _consecutive_fails.get(station_id, 0)


def reset_consecutive_fails(station_id: str) -> None:
    """Reset đếm lỗi liên tiếp khi station có sản phẩm PASS."""
    _consecutive_fails.pop(station_id, None)


def check_and_alert(db: Session, inspection: Inspection) -> Alert | None:
    """Kiểm tra kết quả inspection và tạo alert nếu cần.

    Gọi hàm này SAU KHI inspection đã được tạo trong DB.

    Returns:
        Alert object nếu có alert được tạo, None nếu inspection PASS.
    """
    if inspection.overall_result != "fail":
        # PASS → reset consecutive count
        _consecutive_fails.pop(inspection.station_id, None)
        return None

    alerts_to_create: list[dict] = []

    # ── 1. Alert cho sản phẩm lỗi ──────────────────────────────────────────
    defect_details = _build_defect_details(inspection)
    alerts_to_create.append({
        "alert_type": "defect_detected",
        "severity": "warning",
        "title": f"Sản phẩm lỗi tại {inspection.station_id}",
        "message": (
            f"Serial: {inspection.product_serial}\n"
            f"Loại: {inspection.product_type}\n"
            f"Batch: {inspection.batch_number or 'N/A'}\n"
            f"Lỗi: {defect_details}"
        ),
        "station_id": inspection.station_id,
    })

    # ── 2. Consecutive fail check ──────────────────────────────────────────
    _consecutive_fails[inspection.station_id] = (
        _consecutive_fails.get(inspection.station_id, 0) + 1
    )
    consec = _consecutive_fails[inspection.station_id]

    if consec >= settings.CONSECUTIVE_FAIL_THRESHOLD:
        alerts_to_create.append({
            "alert_type": "consecutive_fail",
            "severity": "critical",
            "title": f"⚠️ {consec} sản phẩm lỗi liên tiếp tại {inspection.station_id}",
            "message": (
                f"Trạm {inspection.station_id} đã có {consec} sản phẩm lỗi liên tiếp!\n"
                f"Sản phẩm mới nhất: {inspection.product_serial}\n"
                f"Vui lòng kiểm tra trạm ngay."
            ),
            "station_id": inspection.station_id,
        })

    # ── 3. Fail rate check (rolling window: last 50 inspections) ───────────
    fail_rate_alert = _check_fail_rate(db, inspection.station_id)
    if fail_rate_alert:
        alerts_to_create.append(fail_rate_alert)

    # ── 4. Save alerts & send Telegram ─────────────────────────────────────
    created_alerts = []
    for alert_data in alerts_to_create:
        alert = Alert(**alert_data)
        db.add(alert)
        db.flush()  # get ID
        created_alerts.append(alert)

    db.commit()
    for a in created_alerts:
        db.refresh(a)

    # Gửi Telegram (best-effort, không block nếu lỗi)
    if created_alerts:
        _send_telegram_alerts(created_alerts)

    # Broadcast WebSocket real-time đến frontend
    if created_alerts:
        _broadcast_ws_alerts(created_alerts)

    # Trả về alert đầu tiên (defect_detected)
    return created_alerts[0] if created_alerts else None


def _build_defect_details(inspection: Inspection) -> str:
    """Tạo mô tả chi tiết các lỗi."""
    parts = []
    if inspection.missing_components:
        try:
            missing = json.loads(inspection.missing_components)
            if missing:
                parts.append(f"Thiếu linh kiện: {', '.join(missing)}")
        except (json.JSONDecodeError, TypeError):
            if inspection.missing_components not in ("[]", "", None):
                parts.append(f"Thiếu linh kiện: {inspection.missing_components}")

    if inspection.qr_result and inspection.qr_result != "pass":
        parts.append(f"QR: {inspection.qr_result}")

    if inspection.sn_result and inspection.sn_result != "pass":
        parts.append(f"SN: {inspection.sn_result}")

    if inspection.antenna_result and inspection.antenna_result != "pass":
        parts.append(f"Anten: {inspection.antenna_result}")

    return "; ".join(parts) if parts else "Không xác định"


def _check_fail_rate(db: Session, station_id: str) -> dict | None:
    """Kiểm tra tỷ lệ lỗi trong 50 inspection gần nhất."""
    recent = (
        db.query(Inspection)
        .filter(Inspection.station_id == station_id)
        .order_by(Inspection.created_at.desc())
        .limit(50)
        .all()
    )

    if len(recent) < 10:  # Chưa đủ data
        return None

    fail_count = sum(1 for r in recent if r.overall_result == "fail")
    fail_rate = fail_count / len(recent)

    if fail_rate >= settings.ALERT_THRESHOLD_RATE:
        return {
            "alert_type": "threshold_exceeded",
            "severity": "critical",
            "title": f"🔴 Tỷ lệ lỗi cao tại {station_id}",
            "message": (
                f"Tỷ lệ lỗi: {fail_rate:.1%} ({fail_count}/{len(recent)} inspection gần nhất)\n"
                f"Ngưỡng cho phép: {settings.ALERT_THRESHOLD_RATE:.1%}\n"
                f"Trạm: {station_id}\n"
                f"Cần kiểm tra ngay!"
            ),
            "station_id": station_id,
        }
    return None


def _send_telegram_alerts(alerts: list[Alert]) -> None:
    """Gửi danh sách alerts qua Telegram (best-effort)."""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        logger.debug("Telegram not configured, skipping notification")
        return

    for alert in alerts:
        severity_emoji = {
            "critical": "🔴",
            "warning": "🟡",
            "info": "ℹ️",
        }.get(alert.severity, "⚪")

        text = (
            f"{severity_emoji} <b>{alert.title}</b>\n"
            f"\n"
            f"{alert.message}\n"
            f"\n"
            f"<i>Thời gian: {alert.created_at.strftime('%H:%M:%S %d/%m/%Y')}</i>"
        )

        _send_telegram_message(token, chat_id, text)


def _send_telegram_message(token: str, chat_id: str, text: str) -> bool:
    """Gửi 1 tin nhắn Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                logger.info(f"Telegram alert sent to {chat_id}")
                return True
            else:
                logger.warning(f"Telegram API error: {resp.status_code} - {resp.text}")
                return False
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False


def _broadcast_ws_alerts(alerts: list[Alert]) -> None:
    """Broadcast alerts qua WebSocket đến tất cả connected clients (best-effort)."""
    try:
        from api.websocket_manager import alert_manager

        for alert in alerts:
            ws_message = {
                "type": "alert",
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "station_id": alert.station_id,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
            }
            # Fire-and-forget: chạy trong background, không block
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(alert_manager.broadcast(ws_message))
            except RuntimeError:
                # Không có event loop đang chạy → chạy sync trong thread
                asyncio.run(alert_manager.broadcast(ws_message))
    except Exception as e:
        logger.error(f"Failed to broadcast WebSocket alert: {e}")
