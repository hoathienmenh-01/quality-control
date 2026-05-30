"""SN Checker - Kiểm tra tem Serial Number"""
import re
import cv2
import numpy as np
from typing import Optional, Tuple

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
            try:
                self.reader = easyocr.Reader(self.languages)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize EasyOCR: {e}")
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

        # Multi-try OCR với nhiều preprocessing
        sn_text, confidence = self.multi_try_ocr(sn_image)

        if sn_text is None:
            return {
                "result": "NOT_READABLE",
                "content": None,
                "error": "Cannot read SN (tem mờ/rách)",
            }

        # Clean up SN text
        # Preserve spaces if SN format expects them (e.g., "SN 123 456")
        preserve_spaces = expected_format and " " in expected_format if expected_format else False
        sn_text = self.clean_sn(sn_text, preserve_spaces=preserve_spaces)

        # Check confidence
        if confidence < 0.4:
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
            "confidence": round(confidence, 4),
            "error": None,
        }

    def read_sn(self, image: np.ndarray) -> Tuple[Optional[str], float]:
        """Đọc SN bằng OCR, trả về (text, confidence)"""
        reader = self._get_reader()
        results = reader.readtext(image)

        if not results:
            return None, 0.0

        # Lấy kết quả có confidence cao nhất
        best = max(results, key=lambda x: x[2])
        return best[1].strip(), best[2]

    def multi_try_ocr(self, image: np.ndarray) -> Tuple[Optional[str], float]:
        """Thử OCR với nhiều preprocessing khác nhau"""
        strategies = [
            ("original", lambda img: img),
            ("gray", lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img),
            ("otsu", self._preprocess_otsu),
            ("adaptive", self._preprocess_adaptive),
            ("deskew_otsu", lambda img: self._preprocess_otsu(self._deskew(img))),
            ("enhanced", self._preprocess_enhanced),
        ]

        best_text = None
        best_confidence = 0.0

        for name, preprocess_fn in strategies:
            try:
                processed = preprocess_fn(image)
                text, confidence = self.read_sn(processed)
                if text and confidence > best_confidence:
                    best_text = text
                    best_confidence = confidence
                    # Nếu confidence > 0.9 thì dừng sớm
                    if confidence > 0.9:
                        break
            except Exception:
                continue

        return best_text, best_confidence

    def _preprocess_otsu(self, image: np.ndarray) -> np.ndarray:
        """Otsu thresholding"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def _preprocess_adaptive(self, image: np.ndarray) -> np.ndarray:
        """Adaptive thresholding"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 15, 4)

    def _preprocess_enhanced(self, image: np.ndarray) -> np.ndarray:
        """CLAHE + adaptive threshold"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """Chỉnh ảnh bị nghiêng"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        # Tìm các điểm trắng
        coords = np.column_stack(np.where(gray < 128))
        if len(coords) < 50:
            return image

        # Tính góc nghiêng
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Chỉ deskew nếu góc > 0.5 độ
        if abs(angle) < 0.5:
            return image

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def crop_roi(self, image: np.ndarray, region: dict) -> np.ndarray:
        """Crop vùng quan tâm"""
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        return image[y : y + h, x : x + w]

    def clean_sn(self, text: str, preserve_spaces: bool = False) -> str:
        """Làm sạch text SN (loại bỏ ký tự lạ)
        
        Args:
            text: SN text từ OCR
            preserve_spaces: Giữ lại space nếu SN format cho phép (VD: "SN 123 456")
        """
        if not text:
            return text
        if preserve_spaces:
            # Giữ lại space cho SN format "SN 123 456"
            cleaned = re.sub(r'[^A-Za-z0-9\-_ ]', '', text)
            # Chuẩn hóa nhiều space thành 1
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        else:
            # Mặc định: loại bỏ tất cả ký tự không phải alphanumeric
            cleaned = re.sub(r'[^A-Za-z0-9\-_]', '', text)
        return cleaned.upper()

    def validate_format(self, sn_text: str, pattern: str) -> bool:
        """Validate SN format"""
        if not sn_text or not pattern:
            return False
        return bool(re.match(pattern, sn_text))

    def check_uniqueness(self, sn_text: str) -> bool:
        """Kiểm tra SN có trùng trong database không
        Returns True nếu SN là duy nhất (chưa tồn tại)
        """
        if not self.db:
            return True  # Không có DB thì coi như unique
        return not self.db.exists_sn(sn_text)

    def enhance_sn_image(self, image: np.ndarray) -> np.ndarray:
        """Cải thiện ảnh tem SN trước khi OCR (backward compatible)"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
