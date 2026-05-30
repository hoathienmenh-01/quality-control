"""SN Checker - Kiểm tra tem Serial Number"""
import re
import cv2
import numpy as np

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False


class SNChecker:
    def __init__(self, db_session=None, languages=["en"]):
        self.db = db_session
        self.reader = None
        self.languages = languages

    def _get_reader(self):
        """Lazy load EasyOCR reader"""
        if self.reader is None:
            if not HAS_EASYOCR:
                raise ImportError("easyocr not installed. Run: pip install easyocr")
            self.reader = easyocr.Reader(self.languages)
        return self.reader

    def check(self, image: np.ndarray, sn_region: dict = None,
              expected_format: str = None) -> dict:
        """Kiểm tra tem Serial Number"""
        # Crop vùng SN nếu có
        if sn_region:
            x, y, w, h = sn_region["x"], sn_region["y"], sn_region["w"], sn_region["h"]
            sn_image = image[y : y + h, x : x + w]
        else:
            sn_image = image

        # Enhance ảnh tem
        enhanced = self.enhance_sn_image(sn_image)

        # OCR đọc text
        sn_text, confidence = self.read_sn(enhanced)

        if sn_text is None:
            return {
                "result": "NOT_READABLE",
                "content": None,
                "error": "Cannot read SN (tem mờ/rách)",
            }

        # Check confidence
        if confidence < 0.5:
            return {
                "result": "NOT_READABLE",
                "content": sn_text,
                "error": f"Low confidence: {confidence:.2f}",
            }

        # Validate format
        if expected_format and not re.match(expected_format, sn_text):
            return {
                "result": "FAIL",
                "content": sn_text,
                "error": f"Format mismatch: expected {expected_format}",
            }

        # Check duplicate
        if self.db and self.db.exists_sn(sn_text):
            return {
                "result": "FAIL",
                "content": sn_text,
                "error": "Duplicate SN",
            }

        return {
            "result": "PASS",
            "content": sn_text,
            "error": None,
        }

    def read_sn(self, image: np.ndarray) -> tuple:
        """Đọc SN bằng OCR, trả về (text, confidence)"""
        reader = self._get_reader()
        results = reader.readtext(image)

        if not results:
            return None, 0.0

        # Lấy kết quả có confidence cao nhất
        best = max(results, key=lambda x: x[2])
        return best[1].strip(), best[2]

    def enhance_sn_image(self, image: np.ndarray) -> np.ndarray:
        """Cải thiện ảnh tem SN trước khi OCR"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
