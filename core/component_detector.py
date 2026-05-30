"""Component Detector - Kiểm tra thiếu linh kiện"""
import cv2
import numpy as np


class ComponentDetector:
    def __init__(self):
        self.templates = {}

    def load_template(self, product_type: str, template_path: str):
        """Load template ảnh chuẩn cho sản phẩm"""
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise ValueError(f"Cannot load template: {template_path}")
        self.templates[product_type] = template

    def detect(self, image: np.ndarray, product_type: str, min_area: int = 100) -> dict:
        """Phát hiện linh kiện trong ảnh"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Tìm contours
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Lọc contours theo kích thước
        components = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                components.append(
                    {"x": x, "y": y, "w": w, "h": h, "area": area}
                )

        # Lấy required components từ template
        required = self.get_required_components(product_type)
        detected = self.match_components(components, required)
        missing = self.find_missing(required, detected)

        return {
            "detected": detected,
            "missing": missing,
            "total_required": len(required),
            "total_detected": len(detected),
            "is_pass": len(missing) == 0,
        }

    def get_required_components(self, product_type: str) -> list:
        """Lấy danh sách linh kiện bắt buộc từ template"""
        # TODO: Load từ database
        default_components = {
            "PCB-A001": ["R1", "R2", "C1", "C2", "IC1", "LED1", "Socket1", "Anten1"],
            "PCB-B002": ["R1", "R2", "R3", "C1", "IC1", "LED1"],
        }
        return default_components.get(product_type, [])

    def match_components(self, detected: list, required: list) -> list:
        """Khớp linh kiện phát hiện với yêu cầu"""
        # Đơn giản: dựa vào số lượng contours
        # TODO: Nâng cấp dựa vào vị trí, kích thước
        return required[: len(detected)]

    def find_missing(self, required: list, detected: list) -> list:
        """Tìm linh kiện thiếu"""
        return [comp for comp in required if comp not in detected]
