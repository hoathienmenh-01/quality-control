"""Camera Manager - Quản lý camera USB/IP"""
import time
import threading
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional


class CameraError(Exception):
    pass


class CameraManager:
    def __init__(self, camera_id=0, resolution=(1920, 1080)):
        self.camera_id = camera_id
        self.resolution = resolution
        self.cap = None
        self._frame_buffer = None
        self._buffer_lock = threading.Lock()
        self._streaming = False
        self._stream_thread = None
        self._reconnect_enabled = True
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 2.0  # seconds
        self._last_frame_time = None

    def connect(self):
        """Kết nối camera (USB hoặc RTSP)"""
        if isinstance(self.camera_id, str) and self.camera_id.startswith(("rtsp://", "http://")):
            self._connect_ip_camera()
        else:
            self._connect_usb_camera()

    def _connect_usb_camera(self):
        """Kết nối USB camera"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise CameraError(f"Cannot connect to camera {self.camera_id}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

    def _connect_ip_camera(self):
        """Kết nối IP camera qua RTSP"""
        # RTSP URL format: rtsp://user:pass@ip:port/stream
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            raise CameraError(f"Cannot connect to IP camera: {self.camera_id}")
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def connect_with_retry(self) -> bool:
        """Kết nối camera với auto-reconnect"""
        for attempt in range(self._max_reconnect_attempts):
            try:
                self.connect()
                return True
            except CameraError:
                if attempt < self._max_reconnect_attempts - 1:
                    time.sleep(self._reconnect_delay)
        return False

    def _auto_reconnect(self):
        """Tự động kết nối lại khi mất connection"""
        if not self._reconnect_enabled:
            return False

        for attempt in range(self._max_reconnect_attempts):
            try:
                self.disconnect()
                self.connect()
                return True
            except CameraError:
                time.sleep(self._reconnect_delay)
        return False

    def capture(self) -> np.ndarray:
        """Chụp 1 ảnh (sử dụng buffer nếu streaming)"""
        if self._streaming and self._frame_buffer is not None:
            with self._buffer_lock:
                if self._frame_buffer is not None:
                    return self._frame_buffer.copy()

        if self.cap is None or not self.cap.isOpened():
            if self._reconnect_enabled:
                if not self._auto_reconnect():
                    raise CameraError("Camera not connected and reconnect failed")
            else:
                raise CameraError("Camera not connected")

        # Flush old frames from buffer
        for _ in range(3):
            self.cap.grab()

        ret, frame = self.cap.read()
        if not ret:
            if self._reconnect_enabled:
                if self._auto_reconnect():
                    ret, frame = self.cap.read()
            if not ret:
                raise CameraError("Cannot capture frame")

        self._last_frame_time = datetime.now()
        return frame

    def capture_to_file(self, directory: str = "captures") -> str:
        """Chụp ảnh và lưu file"""
        frame = self.capture()
        Path(directory).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = f"{directory}/capture_{timestamp}.jpg"
        cv2.imwrite(path, frame)
        return path

    def start_streaming(self):
        """Bắt đầu streaming (chạy background thread)"""
        if self._streaming:
            return

        if self.cap is None or not self.cap.isOpened():
            self.connect()

        self._streaming = True
        self._stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self._stream_thread.start()

    def stop_streaming(self):
        """Dừng streaming"""
        self._streaming = False
        if self._stream_thread:
            self._stream_thread.join(timeout=3.0)
            self._stream_thread = None

    def _stream_loop(self):
        """Background thread liên tục đọc frame"""
        while self._streaming:
            try:
                if self.cap is None or not self.cap.isOpened():
                    if self._reconnect_enabled:
                        self._auto_reconnect()
                    else:
                        break
                    continue

                ret, frame = self.cap.read()
                if ret:
                    with self._buffer_lock:
                        self._frame_buffer = frame
                        self._last_frame_time = datetime.now()
                else:
                    time.sleep(0.1)
            except Exception:
                time.sleep(0.5)

    def get_buffered_frame(self) -> Optional[np.ndarray]:
        """Lấy frame từ buffer (không blocking)"""
        with self._buffer_lock:
            if self._frame_buffer is not None:
                return self._frame_buffer.copy()
        return None

    def trigger_capture(self) -> np.ndarray:
        """Giả lập trigger capture (GPIO simulation)
        Trong thực tế sẽ kết nối với GPIO pin để trigger camera
        """
        # Simulate trigger delay
        time.sleep(0.05)
        return self.capture()

    def disconnect(self):
        """Ngắt kết nối"""
        self.stop_streaming()
        if self.cap:
            self.cap.release()
            self.cap = None

    def is_connected(self) -> bool:
        return self.cap is not None and self.cap.isOpened()

    def get_camera_info(self) -> dict:
        """Lấy thông tin camera"""
        info = {
            "camera_id": self.camera_id,
            "resolution": self.resolution,
            "connected": self.is_connected(),
            "streaming": self._streaming,
            "last_frame_time": self._last_frame_time.isoformat() if self._last_frame_time else None,
        }
        if isinstance(self.camera_id, str):
            info["type"] = "IP" if self.camera_id.startswith(("rtsp://", "http://")) else "file"
        else:
            info["type"] = "USB"
        return info
