"""Anten Checker - Kiểm tra vị trí anten"""
import cv2
import numpy as np
from typing import Optional, Tuple


class AntenChecker:
    def __init__(self):
        # Màu sắc anten: (lower_hsv, upper_hsv, name)
        self.color_ranges = [
            # Đen
            (np.array([0, 0, 0]), np.array([180, 255, 50]), "black"),
            # Trắng
            (np.array([0, 0, 180]), np.array([180, 30, 255]), "white"),
            # Xám
            (np.array([0, 0, 50]), np.array([180, 30, 180]), "gray"),
        ]
        self.min_area = 100
        self.max_area_ratio = 0.3  # Tối đa 30% ảnh

    def check(self, image: np.ndarray, anten_region: dict = None,
              expected_position: dict = None, tolerance: int = 10,
              angle_tolerance: int = 5,
              expected_size: dict = None) -> dict:
        """Kiểm tra vị trí anten"""
        # Crop vùng anten nếu có
        if anten_region:
            x, y, w, h = anten_region["x"], anten_region["y"], anten_region["w"], anten_region["h"]
            anten_image = image[y : y + h, x : x + w]
            offset_x, offset_y = x, y
        else:
            anten_image = image
            offset_x, offset_y = 0, 0

        # Tìm anten theo nhiều màu
        detected = self.detect_anten_multi_color(anten_image)

        if detected is None:
            return {
                "result": "NOT_FOUND",
                "detected_position": None,
                "error": "Anten not found",
            }

        # Tính vị trí thực tế (gốc tọa độ ảnh gốc) với sub-pixel accuracy
        real_x = offset_x + detected["center_x"]
        real_y = offset_y + detected["center_y"]
        detected_angle = detected.get("angle", 0)
        detected_size = {"w": detected["w"], "h": detected["h"]}

        detected_pos = {
            "x": round(real_x, 2),
            "y": round(real_y, 2),
            "angle": detected_angle,
            "size": detected_size,
            "color": detected.get("color", "unknown"),
        }

        # Kiểm tra kích thước
        if expected_size:
            size_result = self._check_size(detected_size, expected_size)
            if size_result:
                return {
                    "result": "FAIL",
                    "detected_position": detected_pos,
                    "error": size_result,
                }

        # So sánh với vị trí chuẩn
        if expected_position:
            dx = abs(real_x - expected_position["x"])
            dy = abs(real_y - expected_position["y"])
            d_angle = abs(detected_angle - expected_position.get("angle", 0))

            if dx > tolerance or dy > tolerance:
                return {
                    "result": "FAIL",
                    "detected_position": detected_pos,
                    "error": f"Position offset: dx={dx:.1f}, dy={dy:.1f}",
                }

            if d_angle > angle_tolerance:
                return {
                    "result": "FAIL",
                    "detected_position": detected_pos,
                    "error": f"Angle offset: {d_angle:.1f}°",
                }

        return {
            "result": "PASS",
            "detected_position": detected_pos,
            "error": None,
        }

    def detect_anten_multi_color(self, image: np.ndarray) -> Optional[dict]:
        """Phát hiện anten theo nhiều màu sắc"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        img_area = image.shape[0] * image.shape[1]
        max_area = img_area * self.max_area_ratio

        best_result = None
        best_area = 0

        for lower, upper, color_name in self.color_ranges:
            mask = cv2.inRange(hsv, lower, upper)

            # Morphological operations để clean up mask
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < self.min_area or area > max_area:
                    continue
                if area > best_area:
                    best_area = area
                    # Sub-pixel center using moments
                    moments = cv2.moments(contour)
                    if moments["m00"] > 0:
                        cx = moments["m10"] / moments["m00"]
                        cy = moments["m01"] / moments["m00"]
                    else:
                        x, y, w, h = cv2.boundingRect(contour)
                        cx, cy = x + w / 2, y + h / 2

                    x, y, w, h = cv2.boundingRect(contour)
                    angle = self.calculate_angle(contour)

                    best_result = {
                        "x": x, "y": y, "w": w, "h": h,
                        "center_x": round(cx, 2),
                        "center_y": round(cy, 2),
                        "area": float(area),
                        "angle": angle,
                        "color": color_name,
                        "contour": contour,
                    }

        # Thử detect theo hình dạng nếu không tìm theo màu
        if best_result is None:
            best_result = self.detect_anten_by_shape(image)

        return best_result

    def detect_anten_by_shape(self, image: np.ndarray) -> Optional[dict]:
        """Phát hiện anten theo hình dạng (hình chữ nhật)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        img_area = image.shape[0] * image.shape[1]
        max_area = img_area * self.max_area_ratio
        best_result = None
        best_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area or area > max_area:
                continue

            # Kiểm tra hình chữ nhật
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) != 4:
                continue

            if area > best_area:
                best_area = area
                moments = cv2.moments(contour)
                if moments["m00"] > 0:
                    cx = moments["m10"] / moments["m00"]
                    cy = moments["m01"] / moments["m00"]
                else:
                    x, y, w, h = cv2.boundingRect(contour)
                    cx, cy = x + w / 2, y + h / 2

                x, y, w, h = cv2.boundingRect(contour)
                angle = self.calculate_angle(contour)

                best_result = {
                    "x": x, "y": y, "w": w, "h": h,
                    "center_x": round(cx, 2),
                    "center_y": round(cy, 2),
                    "area": float(area),
                    "angle": angle,
                    "color": "shape_detected",
                    "contour": contour,
                }

        return best_result

    def detect_anten_by_color(self, image: np.ndarray) -> Optional[dict]:
        """Phát hiện anten theo màu sắc (backward compatible)"""
        result = self.detect_anten_multi_color(image)
        if result is None:
            return None
        return {
            "x": result["x"], "y": result["y"],
            "w": result["w"], "h": result["h"],
            "angle": result["angle"],
        }

    def calculate_angle(self, contour) -> float:
        """Tính góc của contour sử dụng fitEllipse"""
        if len(contour) < 5:
            # Fallback: dùng minimum area rect
            if len(contour) >= 4:
                rect = cv2.minAreaRect(contour)
                return round(rect[2], 2)
            return 0.0
        try:
            ellipse = cv2.fitEllipse(contour)
            angle = ellipse[2]
            # Normalize angle to [-90, 90]
            if angle > 90:
                angle = angle - 180
            return round(angle, 2)
        except cv2.error:
            return 0.0

    def _check_size(self, detected_size: dict, expected_size: dict) -> Optional[str]:
        """Kiểm tra kích thước anten"""
        det_w = detected_size["w"]
        det_h = detected_size["h"]

        min_w = expected_size.get("min_w", 0)
        max_w = expected_size.get("max_w", float("inf"))
        min_h = expected_size.get("min_h", 0)
        max_h = expected_size.get("max_h", float("inf"))

        if det_w < min_w or det_w > max_w:
            return f"Width out of range: {det_w} (expected {min_w}-{max_w})"
        if det_h < min_h or det_h > max_h:
            return f"Height out of range: {det_h} (expected {min_h}-{max_h})"

        return None

    def calculate_position_offset(self, detected: dict, expected: dict) -> dict:
        """Tính toán offset giữa vị trí phát hiện và vị trí kỳ vọng"""
        dx = detected["x"] - expected["x"]
        dy = detected["y"] - expected["y"]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        d_angle = detected.get("angle", 0) - expected.get("angle", 0)

        return {
            "dx": round(dx, 2),
            "dy": round(dy, 2),
            "distance": round(distance, 2),
            "d_angle": round(d_angle, 2),
        }
