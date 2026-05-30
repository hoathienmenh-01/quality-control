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
from .annotator import Annotator


class InspectionPipeline:
    def __init__(self, db_session=None, max_retries: int = 3):
        self.db = db_session
        self.camera = CameraManager()
        self.image_processor = ImageProcessor()
        self.component_detector = ComponentDetector()
        self.qr_checker = QRChecker(db_session)
        self.sn_checker = SNChecker(db_session)
        self.anten_checker = AntenChecker()
        self.annotator = Annotator()
        self.max_retries = max_retries

    def inspect_image(self, image: np.ndarray, product_type: str,
                      station_id: str, batch_number: str = None,
                      template: dict = None,
                      annotate: bool = True) -> dict:
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
            "qr_count": qr_result.get("count", 1),
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

        # Annotate ảnh
        if annotate:
            annotated = self.annotator.annotate_inspection(image, result, template)
            result["annotated_image"] = annotated

        return result

    def inspect_with_retry(self, image: np.ndarray, product_type: str,
                           station_id: str, batch_number: str = None,
                           template: dict = None) -> dict:
        """Kiểm tra với retry logic - nếu FAIL thì thử lại"""
        last_result = None
        for attempt in range(self.max_retries):
            result = self.inspect_image(image, product_type, station_id,
                                        batch_number, template, annotate=False)
            result["attempt"] = attempt + 1
            last_result = result

            if result["overall_result"] == "PASS":
                # Annotate only on final result
                annotated = self.annotator.annotate_inspection(image, result, template)
                result["annotated_image"] = annotated
                return result

            # Chờ 1 chút trước khi retry
            if attempt < self.max_retries - 1:
                time.sleep(0.1)

        # Thất bại sau tất cả retry
        annotated = self.annotator.annotate_inspection(image, last_result, template)
        last_result["annotated_image"] = annotated
        return last_result

    def inspect_from_camera(self, product_type: str, station_id: str,
                            batch_number: str = None, template: dict = None,
                            save_image: bool = True) -> dict:
        """Chụp ảnh từ camera và kiểm tra (với retry)"""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                image = self.camera.capture()
                result = self.inspect_image(image, product_type, station_id,
                                            batch_number, template)
                result["capture_attempt"] = attempt + 1

                if save_image:
                    annotated = result.get("annotated_image", image)
                    path = self.annotator.save_annotated(
                        annotated, "captures",
                        prefix=f"{station_id}_",
                        result=result["overall_result"]
                    )
                    result["image_path"] = path

                return result

            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    time.sleep(0.5)

        return {
            "overall_result": "ERROR",
            "error": f"Camera capture failed after {self.max_retries} attempts: {last_error}",
            "station_id": station_id,
            "inspection_time": datetime.now().isoformat(),
        }

    def batch_inspect(self, images: list, product_type: str, station_id: str,
                      batch_number: str = None, template: dict = None,
                      save_images: bool = False, progress_callback=None) -> list:
        """Kiểm tra nhiều ảnh với progress callback"""
        results = []
        total = len(images)

        for i, image in enumerate(images):
            result = self.inspect_image(image, product_type, station_id,
                                        batch_number, template)
            result["index"] = i
            result["total"] = total
            results.append(result)

            if save_images:
                annotated = result.get("annotated_image", image)
                path = self.annotator.save_annotated(
                    annotated, "captures",
                    prefix=f"{station_id}_batch{i:04d}_",
                    result=result["overall_result"]
                )
                result["image_path"] = path

            if progress_callback:
                progress_callback(i + 1, total, result)

        return results

    def get_summary(self, results: list) -> dict:
        """Tạo summary từ kết quả batch inspection"""
        total = len(results)
        passed = sum(1 for r in results if r.get("overall_result") == "PASS")
        failed = total - passed

        common_missing = {}
        for r in results:
            for comp in r.get("missing_components", []):
                common_missing[comp] = common_missing.get(comp, 0) + 1

        avg_time = sum(r.get("inference_time_ms", 0) for r in results) / total if total else 0

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total else 0,
            "avg_inference_time_ms": round(avg_time, 2),
            "common_missing_components": common_missing,
        }
