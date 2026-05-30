"""Component Detector - Kiểm tra thiếu linh kiện"""
import cv2
import numpy as np
from typing import Optional


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
                shape = self.classify_shape(contour)
                components.append({
                    "x": x, "y": y, "w": w, "h": h,
                    "area": area, "shape": shape,
                })

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
        default_components = {
            "PCB-A001": ["R1", "R2", "C1", "C2", "IC1", "LED1", "Socket1", "Anten1"],
            "PCB-B002": ["R1", "R2", "R3", "C1", "IC1", "LED1"],
        }
        return default_components.get(product_type, [])

    # --- New methods: Template Matching ---

    def template_match(self, image: np.ndarray, template: np.ndarray,
                       threshold: float = 0.8, method: int = cv2.TM_CCOEFF_NORMED) -> list:
        """Template matching cơ bản - trả về list các vị trí match"""
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        gray_tpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template

        result = cv2.matchTemplate(gray_img, gray_tpl, method)
        locations = np.where(result >= threshold)

        h, w = gray_tpl.shape[:2]
        matches = []
        for pt in zip(*locations[::-1]):
            confidence = float(result[pt[1], pt[0]])
            matches.append({
                "x": int(pt[0]),
                "y": int(pt[1]),
                "w": w,
                "h": h,
                "confidence": round(confidence, 4),
            })

        # Non-maximum suppression
        matches = self._nms(matches, overlap_thresh=0.3)
        return matches

    def multi_scale_template_match(self, image: np.ndarray, template: np.ndarray,
                                   scales: list = None, threshold: float = 0.7) -> list:
        """Template matching đa tỷ lệ"""
        if scales is None:
            scales = [0.5, 0.75, 1.0, 1.25, 1.5]

        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        gray_tpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template

        all_matches = []
        for scale in scales:
            # Resize template
            new_w = int(gray_tpl.shape[1] * scale)
            new_h = int(gray_tpl.shape[0] * scale)
            if new_w < 1 or new_h < 1:
                continue
            if new_w > gray_img.shape[1] or new_h > gray_img.shape[0]:
                continue

            scaled_tpl = cv2.resize(gray_tpl, (new_w, new_h))
            result = cv2.matchTemplate(gray_img, scaled_tpl, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)

            for pt in zip(*locations[::-1]):
                confidence = float(result[pt[1], pt[0]])
                all_matches.append({
                    "x": int(pt[0]),
                    "y": int(pt[1]),
                    "w": new_w,
                    "h": new_h,
                    "confidence": round(confidence, 4),
                    "scale": scale,
                })

        all_matches = self._nms(all_matches, overlap_thresh=0.3)
        return sorted(all_matches, key=lambda m: m["confidence"], reverse=True)

    def _nms(self, matches: list, overlap_thresh: float = 0.3) -> list:
        """Non-Maximum Suppression để loại bỏ trùng lặp"""
        if not matches:
            return []

        boxes = np.array([[m["x"], m["y"], m["x"] + m["w"], m["y"] + m["h"]]
                          for m in matches], dtype=np.float32)
        scores = np.array([m["confidence"] for m in matches], dtype=np.float32)

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        areas = (x2 - x1) * (y2 - y1)

        order = scores.argsort()[::-1]
        keep = []

        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            intersection = w * h
            iou = intersection / (areas[i] + areas[order[1:]] - intersection)

            inds = np.where(iou <= overlap_thresh)[0]
            order = order[inds + 1]

        return [matches[i] for i in keep]

    def detect_contours(self, image: np.ndarray, min_area: int = 100,
                        max_area: int = None) -> list:
        """Phát hiện contour-based với lọc diện tích"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 50, 150)
        # Dilate để nối các cạnh đứt
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        results = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            if max_area and area > max_area:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            shape = self.classify_shape(contour)
            results.append({
                "x": x, "y": y, "w": w, "h": h,
                "area": float(area),
                "shape": shape,
                "contour": contour,
            })
        return results

    def classify_shape(self, contour) -> str:
        """Phân loại hình dạng của contour"""
        area = cv2.contourArea(contour)
        if area == 0:
            return "unknown"

        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return "unknown"

        circularity = 4 * np.pi * area / (perimeter * perimeter)

        # Approximate polygon
        epsilon = 0.04 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        num_vertices = len(approx)

        if circularity > 0.85:
            return "circle"
        elif num_vertices == 3:
            return "triangle"
        elif num_vertices == 4:
            # Check if rectangle (aspect ratio)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            if 0.8 <= aspect_ratio <= 1.2:
                return "square"
            return "rectangle"
        elif num_vertices == 5:
            return "pentagon"
        elif num_vertices == 6:
            return "hexagon"
        else:
            if circularity > 0.6:
                return "ellipse"
            return "polygon"

    def match_components(self, detected: list, required: list,
                         tolerance: int = 50) -> list:
        """Khớp linh kiện phát hiện với yêu cầu theo vị trí"""
        matched = []
        used_indices = set()

        for req_name in required:
            best_match = None
            best_idx = -1
            best_score = float("inf")

            # Nếu required có format "Name:x,y" thì dùng position matching
            if ":" in req_name:
                parts = req_name.split(":")
                name = parts[0]
                try:
                    ref_x, ref_y = map(int, parts[1].split(","))
                except (ValueError, IndexError):
                    name = req_name
                    ref_x, ref_y = None, None
            else:
                name = req_name
                ref_x, ref_y = None, None

            if ref_x is not None and ref_y is not None:
                # Position-based matching
                for i, comp in enumerate(detected):
                    if i in used_indices:
                        continue
                    cx = comp["x"] + comp["w"] // 2
                    cy = comp["y"] + comp["h"] // 2
                    dist = ((cx - ref_x) ** 2 + (cy - ref_y) ** 2) ** 0.5
                    if dist < tolerance and dist < best_score:
                        best_score = dist
                        best_match = comp
                        best_idx = i

            if best_match is None:
                # No fallback — mark as not found
                pass

            if best_match is not None:
                used_indices.add(best_idx)
                matched.append({
                    "name": name,
                    "position": {"x": best_match["x"], "y": best_match["y"],
                                 "w": best_match["w"], "h": best_match["h"]},
                    "confidence": best_match.get("confidence", 1.0),
                    "found": True,
                    "shape": best_match.get("shape", "unknown"),
                })
            else:
                matched.append({
                    "name": name,
                    "position": None,
                    "confidence": 0.0,
                    "found": False,
                    "shape": None,
                })

        return matched

    def find_missing(self, required: list, detected: list) -> list:
        """Tìm linh kiện thiếu"""
        return [comp["name"] for comp in detected if not comp["found"]]
