"""Tests for notification service — alert creation logic."""

import pytest
from unittest.mock import patch, MagicMock

from services.notification_service import (
    check_and_alert,
    _build_defect_details,
    _check_fail_rate,
    get_consecutive_fails,
    reset_consecutive_fails,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

class FakeInspection:
    """Mock inspection object."""
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.overall_result = kwargs.get("overall_result", "fail")
        self.product_serial = kwargs.get("product_serial", "SN001")
        self.product_type = kwargs.get("product_type", "PCB-A001")
        self.batch_number = kwargs.get("batch_number", "B001")
        self.station_id = kwargs.get("station_id", "ST01")
        self.missing_components = kwargs.get("missing_components", '["R1"]')
        self.qr_result = kwargs.get("qr_result", "fail")
        self.sn_result = kwargs.get("sn_result", "pass")
        self.antenna_result = kwargs.get("antenna_result", "pass")
        self.created_at = kwargs.get("created_at", None)


# ── Tests: _build_defect_details ─────────────────────────────────────────────

class TestBuildDefectDetails:
    def test_missing_components_and_qr_fail(self):
        insp = FakeInspection(
            missing_components='["R1", "C1"]',
            qr_result="fail",
            sn_result="pass",
            antenna_result="pass",
        )
        details = _build_defect_details(insp)
        assert "R1" in details
        assert "C1" in details
        assert "QR" in details

    def test_all_pass_but_overall_fail(self):
        insp = FakeInspection(
            overall_result="fail",
            missing_components="[]",
            qr_result="pass",
            sn_result="pass",
            antenna_result="pass",
        )
        details = _build_defect_details(insp)
        # No specific defects, should return fallback
        assert details == "Không xác định"

    def test_sn_error_only(self):
        insp = FakeInspection(
            overall_result="fail",
            missing_components=None,
            qr_result="pass",
            sn_result="not_readable",
            antenna_result="pass",
        )
        details = _build_defect_details(insp)
        assert "SN: not_readable" in details

    def test_antenna_error(self):
        insp = FakeInspection(
            overall_result="fail",
            missing_components=None,
            qr_result="pass",
            sn_result="pass",
            antenna_result="fail",
        )
        details = _build_defect_details(insp)
        assert "Anten: fail" in details

    def test_multiple_errors(self):
        insp = FakeInspection(
            overall_result="fail",
            missing_components='["IC1"]',
            qr_result="not_found",
            sn_result="fail",
            antenna_result="fail",
        )
        details = _build_defect_details(insp)
        assert "IC1" in details
        assert "QR" in details
        assert "SN" in details
        assert "Anten" in details


# ── Tests: get/reset consecutive fails ───────────────────────────────────────

class TestConsecutiveFails:
    def setup_method(self):
        """Reset state before each test."""
        reset_consecutive_fails("ST01")

    def test_initial_count_is_zero(self):
        assert get_consecutive_fails("ST01") == 0

    def test_reset(self):
        from services import notification_service
        notification_service._consecutive_fails["ST01"] = 5
        reset_consecutive_fails("ST01")
        assert get_consecutive_fails("ST01") == 0


# ── Tests: check_and_alert with PASS ─────────────────────────────────────────

class TestCheckAndAlertPass:
    def test_pass_returns_none(self):
        """PASS inspection should not create alert."""
        insp = FakeInspection(overall_result="pass")
        db = MagicMock()
        result = check_and_alert(db, insp)
        assert result is None
        db.add.assert_not_called()


# ── Tests: check_and_alert with FAIL ─────────────────────────────────────────

class TestCheckAndAlertFail:
    def setup_method(self):
        reset_consecutive_fails("ST01")

    @patch("services.notification_service._send_telegram_alerts")
    def test_fail_creates_defect_alert(self, mock_telegram):
        """FAIL inspection should create a defect_detected alert."""
        insp = FakeInspection(overall_result="fail")
        db = MagicMock()
        alert = check_and_alert(db, insp)
        assert alert is not None
        assert alert.alert_type == "defect_detected"
        assert alert.severity == "warning"
        assert "ST01" in alert.title

    @patch("services.notification_service._send_telegram_alerts")
    def test_consecutive_fail_triggers_critical(self, mock_telegram):
        """After threshold consecutive fails, should create critical alert."""
        from config import settings
        # Simulate consecutive fails
        from services import notification_service
        notification_service._consecutive_fails["ST01"] = settings.CONSECUTIVE_FAIL_THRESHOLD - 1

        insp = FakeInspection(overall_result="fail")
        db = MagicMock()
        alerts = []
        # capture all alerts added to db
        def capture_add(obj):
            if hasattr(obj, "alert_type"):
                alerts.append(obj)
        db.add.side_effect = capture_add

        check_and_alert(db, insp)

        # Should have 2 alerts: defect_detected + consecutive_fail
        assert len(alerts) == 2
        types = {a.alert_type for a in alerts}
        assert "defect_detected" in types
        assert "consecutive_fail" in types
