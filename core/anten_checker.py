"""Anten Checker - Kiểm tra vị trí anten"""
import cv2
import numpy as np


class AntenChecker:
    def __init__(self):
        pass

    def check(self, image: np.ndarray, anten_region: dict = None,
              expected_position: dict = None, tolerance: int = 10,
              angle_tolerance: int = 5) -> dict:
        """Kiểm tra vị trí anten"""
        # Crop vùng anten nếu có
        if anten_region:
            x, y, w, h = anten_region["x"], anten_region["y"], anten_region["w"], anten_region["h"]
            anten_image = image[y : y + h, x : x + w]
            offset_x, offset_y = x, y
        else:
            anten_image = image
            offset_x, offset_y = 0, 0

        # Tìm anten theo màu sắc
        detected = self.detect_anten_by_color(anten_image)

        if detected is None:
            return {
                "result": "NOT_FOUND",
                "detected_position": None,
                "error": "Anten not found",
            }

        # Tính vị trí thực tế (gốc tọa độ ảnh gốc)
        real_x = offset_x + detected["x"]
        real_y = offset_y + detected["y"]
        detected_angle = detected.get("angle", 0)

        detected_pos = {"x": real_x, "y": real_y, "angle": detected_angle}

        # So sánh với vị trí chuẩn
        if expected_position:
            dx = abs(real_x - expected_position["x"])
            dy = abs(real_y - expected_position["y"])
            d_angle = abs(detected_angle - expected_position.get("angle", 0))

            if dx > tolerance or dy > tolerance:
                return {
                    "result": "FAIL",
                    "detected_position": detected_pos,
                    "error": f"Position offset: dx={dx}, dy={dy}",
                }

            if d_angle > angle_tolerance:
                return {
                    "result": "FAIL",
                    "detected_position": detected_pos,
                    "error": f"Angle offset: {d_angle}°",
                }

        return {
            "result": "PASS",
            "detected_position": detected_pos,
            "error": None,
        }

    def detect_anten_by_color(self, image: np.ndarray) -> dict | None:
        """Phát hiện anten theo màu sắc"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Mask màu đen (anten thường màu đen)
        lower = np.array([0, 0, 0])
        upper = np.array([180, 255, 50])
        mask = cv2.inRange(hsv, lower, upper)

        # Tìm contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Lấy contour lớn nhất
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)

        # Tính góc
        angle = self.calculate_angle(largest)

        return {"x": x, "y": y, "w": w, "h": h, "angle": angle}

    def calculate_angle(self, contour) -> float:
        """Tính góc của contour"""
        if len(contour) < 5:
            return 0.0
        _, _, angle = cv2.fitEllipse(contour)
        return round(angle, 2)
