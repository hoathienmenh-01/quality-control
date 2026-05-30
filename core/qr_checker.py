"""QR Checker - Kiểm tra mã QR"""
import re
import cv2
import numpy as np

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False


class QRChecker:
    def __init__(self, db_session=None):
        self.db = db_session

    def check(self, image: np.ndarray, expected_format: str = None,
              batch_number: str = None) -> dict:
        """Kiểm tra mã QR"""
        # Đọc QR
        qr_content = self.read_qr(image)

        if qr_content is None:
            return {
                "result": "NOT_FOUND",
                "content": None,
                "error": "QR not found in image",
            }

        # Validate format
        if expected_format and not re.match(expected_format, qr_content):
            return {
                "result": "FAIL",
                "content": qr_content,
                "error": f"Format mismatch: expected {expected_format}",
            }

        # Check batch
        if batch_number and batch_number not in qr_content:
            return {
                "result": "FAIL",
                "content": qr_content,
                "error": f"Batch mismatch: expected {batch_number}",
            }

        # Check duplicate
        if self.db and self.db.exists_qr(qr_content):
            return {
                "result": "FAIL",
                "content": qr_content,
                "error": "Duplicate QR (tem dán nhầm)",
            }

        return {
            "result": "PASS",
            "content": qr_content,
            "error": None,
        }

    def read_qr(self, image: np.ndarray) -> str | None:
        """Đọc QR code từ ảnh"""
        if not HAS_PYZBAR:
            raise ImportError("pyzbar not installed. Run: pip install pyzbar")

        decoded = pyzbar_decode(image)
        if not decoded:
            return None
        return decoded[0].data.decode("utf-8")
