"""Annotator - Vẽ kết quả kiểm tra lên ảnh"""
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime


class Annotator:
    """Vẽ bounding boxes, text, markers lên ảnh kết quả inspection"""

    # Colors (BGR)
    COLOR_PASS = (0, 200, 0)       # Xanh lá
    COLOR_FAIL = (0, 0, 200)       # Đỏ
    COLOR_WARNING = (0, 165, 255)  # Cam
    COLOR_INFO = (200, 200, 0)     # Cyan
    COLOR_MISSING = (0, 0, 255)    # Đỏ đậm
    COLOR_DETECTED = (0, 255, 0)   # Xanh lá đậm
    COLOR_ANTEN = (255, 0, 255)    # Tím
    COLOR_QR = (255, 255, 0)       # Vàng
    COLOR_SN = (0, 255, 255)       # Vàng nhạt

    def __init__(self, font_scale: float = 0.6, thickness: int = 2):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = font_scale
        self.thickness = thickness

    def annotate_inspection(self, image: np.ndarray, result: dict,
                            template: dict = None) -> np.ndarray:
        """Vẽ toàn bộ kết quả inspection lên ảnh"""
        annotated = image.copy()

        # Vẽ overall PASS/FAIL
        self._draw_overall_result(annotated, result["overall_result"])

        # Vẽ component results
        self._draw_components(annotated, result)

        # Vẽ QR region
        if template and "qr_region" in template:
            self._draw_region(annotated, template["qr_region"],
                              "QR", self.COLOR_QR)
            if result.get("qr_content"):
                self._draw_text_at(annotated, result["qr_region"],
                                   f"QR: {result['qr_content'][:30]}",
                                   self.COLOR_QR)

        # Vẽ SN region
        if template and "sn_region" in template:
            self._draw_region(annotated, template["sn_region"],
                              "SN", self.COLOR_SN)
            if result.get("sn_content"):
                self._draw_text_at(annotated, template["sn_region"],
                                   f"SN: {result['sn_content'][:30]}",
                                   self.COLOR_SN)

        # Vẽ anten position
        if result.get("antenna_detected_position"):
            self._draw_anten_marker(annotated, result["antenna_detected_position"])

        # Vẽ expected anten position từ template
        if template and "antenna_position" in template:
            self._draw_crosshair(annotated, template["antenna_position"],
                                 self.COLOR_WARNING, "Expected")

        return annotated

    def draw_bounding_box(self, image: np.ndarray, x: int, y: int,
                          w: int, h: int, label: str = "",
                          color: tuple = None, confidence: float = None) -> np.ndarray:
        """Vẽ bounding box với label"""
        if color is None:
            color = self.COLOR_DETECTED
        annotated = image.copy()

        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, self.thickness)

        # Label text
        text = label
        if confidence is not None:
            text += f" ({confidence:.2f})"

        if text:
            self._put_text(annotated, text, (x, y - 5), color)

        return annotated

    def draw_pass_fail(self, image: np.ndarray, result: str,
                       position: tuple = None) -> np.ndarray:
        """Vẽ PASS/FAIL text lớn"""
        annotated = image.copy()
        color = self.COLOR_PASS if result == "PASS" else self.COLOR_FAIL
        text = f"  {result}  "

        if position is None:
            # Vẽ ở góc trên phải
            h, w = annotated.shape[:2]
            position = (w - 200, 40)

        # Background rectangle
        (text_w, text_h), baseline = cv2.getTextSize(
            text, self.font, 1.2, 3
        )
        x, y = position
        cv2.rectangle(annotated, (x - 5, y - text_h - 5),
                      (x + text_w + 5, y + baseline + 5), color, -1)

        # Text
        cv2.putText(annotated, text, (x, y),
                    self.font, 1.2, (255, 255, 255), 3, cv2.LINE_AA)

        return annotated

    def draw_qr_content(self, image: np.ndarray, qr_content: str,
                        region: dict = None) -> np.ndarray:
        """Vẽ QR content lên ảnh"""
        annotated = image.copy()
        if region:
            self._draw_region(annotated, region, "QR", self.COLOR_QR)
            pos = (region["x"], region["y"] - 10)
        else:
            pos = (10, 60)
        self._put_text(annotated, f"QR: {qr_content}", pos, self.COLOR_QR)
        return annotated

    def draw_sn_content(self, image: np.ndarray, sn_content: str,
                        region: dict = None) -> np.ndarray:
        """Vẽ SN content lên ảnh"""
        annotated = image.copy()
        if region:
            self._draw_region(annotated, region, "SN", self.COLOR_SN)
            pos = (region["x"], region["y"] - 10)
        else:
            pos = (10, 90)
        self._put_text(annotated, f"SN: {sn_content}", pos, self.COLOR_SN)
        return annotated

    def draw_anten_marker(self, image: np.ndarray, position: dict,
                          color: tuple = None) -> np.ndarray:
        """Vẽ marker cho vị trí anten"""
        annotated = image.copy()
        if color is None:
            color = self.COLOR_ANTEN

        x = int(position["x"])
        y = int(position["y"])

        # Crosshair
        cv2.drawMarker(annotated, (x, y), color,
                       cv2.MARKER_CROSS, 30, 2)

        # Vòng tròn
        cv2.circle(annotated, (x, y), 15, color, 2)

        # Label
        label = f"Anten ({x},{y})"
        if "angle" in position:
            label += f" {position['angle']:.1f}°"
        self._put_text(annotated, label, (x + 20, y - 10), color)

        return annotated

    def draw_component_results(self, image: np.ndarray,
                               components: list) -> np.ndarray:
        """Vẽ kết quả phát hiện linh kiện"""
        annotated = image.copy()

        for comp in components:
            if not comp.get("found", True):
                continue
            pos = comp.get("position")
            if not pos:
                continue

            color = self.COLOR_DETECTED if comp.get("found") else self.COLOR_MISSING
            label = comp.get("name", "Component")

            cv2.rectangle(annotated,
                          (pos["x"], pos["y"]),
                          (pos["x"] + pos["w"], pos["y"] + pos["h"]),
                          color, self.thickness)

            self._put_text(annotated, label,
                           (pos["x"], pos["y"] - 5), color)

        return annotated

    def save_annotated(self, image: np.ndarray, output_dir: str = "captures",
                       prefix: str = "", result: str = "UNKNOWN") -> str:
        """Lưu ảnh đã annotate"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{prefix}{result}_{timestamp}.jpg" if prefix else f"{result}_{timestamp}.jpg"
        path = str(Path(output_dir) / filename)
        cv2.imwrite(path, image)
        return path

    # --- Internal methods ---

    def _draw_overall_result(self, image: np.ndarray, result: str):
        """Vẽ PASS/FAIL ở góc trên phải"""
        color = self.COLOR_PASS if result == "PASS" else self.COLOR_FAIL
        text = f"  {result}  "
        h_img, w_img = image.shape[:2]

        (tw, th), baseline = cv2.getTextSize(text, self.font, 1.2, 3)
        x = w_img - tw - 20
        y = 40

        # Background
        cv2.rectangle(image, (x - 5, y - th - 5),
                      (x + tw + 5, y + baseline + 5), color, -1)
        cv2.putText(image, text, (x, y),
                    self.font, 1.2, (255, 255, 255), 3, cv2.LINE_AA)

    def _draw_components(self, image: np.ndarray, result: dict):
        """Vẽ component detection results"""
        for comp in result.get("detected_components", []):
            if not isinstance(comp, dict):
                continue
            if not comp.get("found", True):
                continue
            pos = comp.get("position")
            if not pos:
                continue

            color = self.COLOR_DETECTED
            label = comp.get("name", "?")

            cv2.rectangle(image,
                          (pos["x"], pos["y"]),
                          (pos["x"] + pos["w"], pos["y"] + pos["h"]),
                          color, self.thickness)
            self._put_text(image, label, (pos["x"], pos["y"] - 5), color)

        # Mark missing
        for comp in result.get("detected_components", []):
            if isinstance(comp, dict) and not comp.get("found", True):
                name = comp.get("name", "?")
                self._put_text(image, f"MISSING: {name}", (10, 120 + 25 * result.get("detected_components", []).index(comp)),
                               self.COLOR_MISSING)

    def _draw_region(self, image: np.ndarray, region: dict,
                     label: str, color: tuple):
        """Vẽ rectangle cho region"""
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        cv2.rectangle(image, (x, y), (x + w, y + h), color, self.thickness)
        self._put_text(image, label, (x, y - 5), color)

    def _draw_text_at(self, image: np.ndarray, region: dict,
                      text: str, color: tuple):
        """Vẽ text dưới region"""
        x = region["x"]
        y = region["y"] + region["h"] + 20
        self._put_text(image, text, (x, y), color)

    def _draw_crosshair(self, image: np.ndarray, position: dict,
                        color: tuple, label: str = ""):
        """Vẽ crosshair tại vị trí"""
        x = int(position["x"])
        y = int(position["y"])
        cv2.drawMarker(image, (x, y), color, cv2.MARKER_CROSS, 25, 2)
        cv2.circle(image, (x, y), 12, color, 2)
        if label:
            self._put_text(image, label, (x + 15, y - 10), color)

    def _put_text(self, image: np.ndarray, text: str,
                  position: tuple, color: tuple):
        """Vẽ text với background để dễ đọc"""
        x, y = position
        # Clamp y
        if y < 15:
            y = 15

        (tw, th), baseline = cv2.getTextSize(
            text, self.font, self.font_scale, self.thickness
        )

        # Background
        cv2.rectangle(image,
                      (x - 2, y - th - 4),
                      (x + tw + 2, y + baseline + 2),
                      (0, 0, 0), -1)

        cv2.putText(image, text, (x, y),
                    self.font, self.font_scale, color,
                    self.thickness, cv2.LINE_AA)
