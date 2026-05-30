"""Unit tests for component detector"""
import pytest
import numpy as np
import cv2


def create_test_image(width=640, height=480):
    """Tạo ảnh test giả"""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (200, 200), (255, 255, 255), -1)
    cv2.rectangle(img, (300, 150), (400, 250), (200, 200, 200), -1)
    return img


class TestComponentDetector:
    def test_detect_returns_dict(self):
        from core.component_detector import ComponentDetector
        detector = ComponentDetector()
        img = create_test_image()
        result = detector.detect(img, "PCB-A001")
        assert isinstance(result, dict)
        assert "detected" in result
        assert "missing" in result
        assert "is_pass" in result

    def test_detect_with_unknown_product(self):
        from core.component_detector import ComponentDetector
        detector = ComponentDetector()
        img = create_test_image()
        result = detector.detect(img, "UNKNOWN")
        assert isinstance(result, dict)

    def test_templates_attribute_exists(self):
        from core.component_detector import ComponentDetector
        detector = ComponentDetector()
        assert hasattr(detector, 'templates')
        assert isinstance(detector.templates, dict)


class TestImageProcessor:
    def test_preprocess(self):
        from core.image_processor import ImageProcessor
        processor = ImageProcessor()
        img = create_test_image()
        result = processor.preprocess(img)
        assert result is not None
        assert result.shape[0] > 0

    def test_resize(self):
        from core.image_processor import ImageProcessor
        processor = ImageProcessor()
        img = create_test_image()
        result = processor.resize(img)
        assert result.shape[0] > 0
        assert result.shape[1] > 0

    def test_to_grayscale(self):
        from core.image_processor import ImageProcessor
        processor = ImageProcessor()
        img = create_test_image()
        result = processor.to_grayscale(img)
        assert len(result.shape) == 2

    def test_crop_roi(self):
        from core.image_processor import ImageProcessor
        processor = ImageProcessor()
        img = create_test_image()
        result = processor.crop_roi(img, 50, 50, 200, 200)
        assert result.shape[0] == 200
        assert result.shape[1] == 200


class TestQRChecker:
    def test_check_no_qr(self):
        from core.qr_checker import QRChecker, HAS_PYZBAR
        checker = QRChecker()
        img = create_test_image()
        if not HAS_PYZBAR:
            pytest.skip("pyzbar not installed")
        result = checker.check(img)
        assert result["result"] in ["PASS", "FAIL", "NOT_READABLE"]


class TestSNChecker:
    def test_check_init(self):
        from core.sn_checker import SNChecker
        checker = SNChecker()
        assert checker is not None


class TestAntenChecker:
    def test_check_no_anten(self):
        from core.anten_checker import AntenChecker
        checker = AntenChecker()
        img = create_test_image()
        result = checker.check(img)
        assert result["result"] in ["PASS", "FAIL", "NOT_FOUND"]


class TestPipeline:
    def test_inspect_image(self):
        from core.pipeline import InspectionPipeline
        from core.qr_checker import HAS_PYZBAR
        if not HAS_PYZBAR:
            pytest.skip("pyzbar not installed")
        pipeline = InspectionPipeline()
        img = create_test_image()
        result = pipeline.inspect_image(img, "PCB-A001", "STATION-01")
        assert "overall_result" in result
        assert result["overall_result"] in ["PASS", "FAIL"]
        assert "inference_time_ms" in result
