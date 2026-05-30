"""Camera Manager - Quản lý camera USB/IP"""
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path


class CameraError(Exception):
    pass


class CameraManager:
    def __init__(self, camera_id=0, resolution=(1920, 1080)):
        self.camera_id = camera_id
        self.resolution = resolution
        self.cap = None

    def connect(self):
        """Kết nối camera"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise CameraError(f"Cannot connect to camera {self.camera_id}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

    def capture(self) -> np.ndarray:
        """Chụp 1 ảnh"""
        if self.cap is None or not self.cap.isOpened():
            raise CameraError("Camera not connected")
        ret, frame = self.cap.read()
        if not ret:
            raise CameraError("Cannot capture frame")
        return frame

    def capture_to_file(self, directory: str = "captures") -> str:
        """Chụp ảnh và lưu file"""
        frame = self.capture()
        Path(directory).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = f"{directory}/capture_{timestamp}.jpg"
        cv2.imwrite(path, frame)
        return path

    def disconnect(self):
        """Ngắt kết nối"""
        if self.cap:
            self.cap.release()
            self.cap = None

    def is_connected(self) -> bool:
        return self.cap is not None and self.cap.isOpened()
