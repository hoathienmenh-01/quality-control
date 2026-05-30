"""Inspection Pipeline - Kết hợp tất cả detectors"""
import time
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np

from .camera import CameraManager
from .image_processor import ImageProcessor
from .component_detector import ComponentDetector
from .qr_checker import QRChecker
from .sn_checker import SNChecker
from .anten_checker import AntenChecker


class InspectionPipeline:
    def __init__(self, db_session=None):
        self.db = db_session
        self.camera = CameraManager()
        self.image_processor = ImageProcessor()
        self.component_detector = ComponentDetector()
        self.qr_checker = QRChecker(db_session)
        self.sn_checker = SNChecker(db_session)
        self.anten_checker = AntenChecker()

    def inspect_image(self, image: np.ndarray, product_type: str,
                      station_id: str, batch_number: str = None,
                      template: dict = None) -> dict:
        """Chạy toàn bộ kiểm tra cho 1 ảnh"""
        start_time = time.time()

        # Preprocess ảnh
        processed = self.image_processor.preprocess(image)

        # 1. Kiểm tra linh kiện
        component_result = self.component_detector.detect(processed, product_type)

        # 2. Kiểm tra QR
        qr_region = (template or {}).get("qr_region")
        qr_result = self.qr_checker.check(
            self.image_processor.crop_roi(processed, **qr_region) if qr_region else processed,
            expected_format=(template or {}).get("qr_format"),
            batch_number=batch_number,
        )

        # 3. Kiểm tra SN
        sn_region = (template or {}).get("sn_region")
        sn_result = self.sn_checker.check(
            processed,
            sn_region=sn_region,
            expected_format=(template or {}).get("sn_format"),
        )

        # 4. Kiểm tra Anten
        anten_region = (template or {}).get("anten_region")
        anten_result = self.anten_checker.check(
            processed,
            anten_region=anten_region,
            expected_position=(template or {}).get("antenna_position"),
        )

        # Tổng hợp kết quả
        overall = "PASS"
        if (
            not component_result["is_pass"]
            or qr_result["result"] != "PASS"
            or sn_result["result"] != "PASS"
            or anten_result["result"] != "PASS"
        ):
            overall = "FAIL"

        inference_time = (time.time() - start_time) * 1000  # ms

        # Tạo kết quả
        result = {
            "overall_result": overall,
            "product_type": product_type,
            "station_id": station_id,
            "batch_number": batch_number,
            "missing_components": component_result["missing"],
            "detected_components": component_result["detected"],
            "qr_result": qr_result["result"],
            "qr_content": qr_result["content"],
            "qr_error_detail": qr_result["error"],
            "sn_result": sn_result["result"],
            "sn_content": sn_result["content"],
            "sn_error_detail": sn_result["error"],
            "antenna_result": anten_result["result"],
            "antenna_detected_position": anten_result["detected_position"],
            "antenna_error_detail": anten_result["error"],
            "inference_time_ms": round(inference_time, 2),
            "inspection_time": datetime.now().isoformat(),
        }

        return result

    def inspect_from_camera(self, product_type: str, station_id: str,
                            batch_number: str = None, template: dict = None,
                            save_image: bool = True) -> dict:
        """Chụp ảnh từ camera và kiểm tra"""
        # Chụp ảnh
        image = self.camera.capture()

        # Chạy kiểm tra
        result = self.inspect_image(image, product_type, station_id, batch_number, template)

        # Lưu ảnh
        if save_image:
            Path("captures").mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            image_path = f"captures/{result['overall_result']}_{timestamp}.jpg"
            cv2.imwrite(image_path, image)
            result["image_path"] = image_path

        return result

    def batch_inspect(self, images: list, product_type: str, station_id: str,
                      batch_number: str = None, template: dict = None) -> list:
        """Kiểm tra nhiều ảnh"""
        results = []
        for image in images:
            result = self.inspect_image(image, product_type, station_id, batch_number, template)
            results.append(result)
        return results
