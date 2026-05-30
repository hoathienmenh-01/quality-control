"""QR Checker - Kiểm tra mã QR"""
import re
import cv2
import numpy as np
from typing import Optional

try:
    from pyzbar.pyzbar import decode as pyzbar_decode, ZBarSymbol
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False


class QRChecker:
    def __init__(self, db_session=None):
        self.db = db_session

    def check(self, image: np.ndarray, expected_format: str = None,
              batch_number: str = None) -> dict:
        """Kiểm tra mã QR (single)"""
        qr_contents = self.read_all_qrs(image)

        if not qr_contents:
            return {
                "result": "NOT_FOUND",
                "content": None,
                "contents": [],
                "count": 0,
                "error": "QR not found in image",
            }

        # Validate format
        if expected_format:
            for content in qr_contents:
                if not re.match(expected_format, content):
                    return {
                        "result": "FAIL",
                        "content": content,
                        "contents": qr_contents,
                        "count": len(qr_contents),
                        "error": f"Format mismatch: expected {expected_format}",
                    }

        # Check batch
        if batch_number:
            found_batch = any(batch_number in c for c in qr_contents)
            if not found_batch:
                return {
                    "result": "FAIL",
                    "content": qr_contents[0],
                    "contents": qr_contents,
                    "count": len(qr_contents),
                    "error": f"Batch mismatch: expected {batch_number}",
                }

        # Check duplicate
        if self.db:
            for content in qr_contents:
                if self.db.exists_qr(content):
                    return {
                        "result": "FAIL",
                        "content": content,
                        "contents": qr_contents,
                        "count": len(qr_contents),
                        "error": "Duplicate QR (tem dán nhầm)",
                    }

        return {
            "result": "PASS",
            "content": qr_contents[0],
            "contents": qr_contents,
            "count": len(qr_contents),
            "error": None,
        }

    def read_qr(self, image: np.ndarray) -> Optional[str]:
        """Đọc 1 QR code từ ảnh (backward compatible)"""
        results = self.read_all_qrs(image)
        return results[0] if results else None

    def read_all_qrs(self, image: np.ndarray) -> list:
        """Đọc tất cả QR codes từ ảnh"""
        if not HAS_PYZBAR:
            raise ImportError("pyzbar not installed. Run: pip install pyzbar")

        decoded = pyzbar_decode(image, symbols=[ZBarSymbol.QRCODE])
        contents = []
        for obj in decoded:
            try:
                text = obj.data.decode("utf-8")
                if text and text not in contents:
                    contents.append(text)
            except UnicodeDecodeError:
                continue
        return contents

    def read_qr_from_region(self, image: np.ndarray, region: dict) -> Optional[str]:
        """Đọc QR từ vùng cụ thể (crop trước khi decode)"""
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        cropped = image[y : y + h, x : x + w]
        results = self.read_all_qrs(cropped)
        return results[0] if results else None

    def read_all_qrs_from_region(self, image: np.ndarray, region: dict) -> list:
        """Đọc tất cả QR từ vùng cụ thể"""
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        cropped = image[y : y + h, x : x + w]
        return self.read_all_qrs(cropped)

    def validate_format(self, content: str, pattern: str) -> bool:
        """Validate QR content against regex pattern"""
        if not content or not pattern:
            return False
        return bool(re.match(pattern, content))

    def parse_qr_content(self, content: str, separator: str = "|") -> dict:
        """Parse QR content thành các trường
        VD: 'SN:ABC123|BATCH:001|DATE:2024-01-01' → {SN: ABC123, BATCH: 001, DATE: ...}
        """
        fields = {}
        if not content:
            return fields

        parts = content.split(separator)
        for part in parts:
            part = part.strip()
            if ":" in part:
                key, value = part.split(":", 1)
                fields[key.strip()] = value.strip()
            elif "=" in part:
                key, value = part.split("=", 1)
                fields[key.strip()] = value.strip()
            else:
                # Không có key, dùng index
                fields[f"field_{len(fields)}"] = part

        return fields

    def batch_validate(self, images: list, expected_format: str = None,
                       batch_number: str = None) -> list:
        """Kiểm tra QR cho nhiều ảnh"""
        results = []
        for i, image in enumerate(images):
            result = self.check(image, expected_format=expected_format,
                                batch_number=batch_number)
            result["index"] = i
            results.append(result)
        return results

    def check_with_preprocessing(self, image: np.ndarray,
                                  expected_format: str = None,
                                  batch_number: str = None) -> dict:
        """Kiểm tra QR với nhiều preprocessing attempts"""
        # Thử đọc trực tiếp
        result = self.check(image, expected_format=expected_format,
                            batch_number=batch_number)
        if result["result"] != "NOT_FOUND":
            return result

        # Thử grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        result = self.check(gray, expected_format=expected_format,
                            batch_number=batch_number)
        if result["result"] != "NOT_FOUND":
            return result

        # Thử tăng contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        result = self.check(enhanced, expected_format=expected_format,
                            batch_number=batch_number)
        if result["result"] != "NOT_FOUND":
            return result

        # Thử threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        result = self.check(thresh, expected_format=expected_format,
                            batch_number=batch_number)
        return result
