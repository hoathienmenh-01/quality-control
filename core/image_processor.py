"""Image Processor - Xử lý ảnh trước khi phân tích"""
import cv2
import numpy as np


class ImageProcessor:
    def __init__(self, target_size=(1920, 1080)):
        self.target_size = target_size

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Xử lý ảnh trước khi phân tích"""
        image = self.resize(image)
        image = self.normalize_brightness(image)
        image = self.denoise(image)
        return image

    def resize(self, image: np.ndarray) -> np.ndarray:
        return cv2.resize(image, self.target_size)

    def normalize_brightness(self, image: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def denoise(self, image: np.ndarray) -> np.ndarray:
        return cv2.GaussianBlur(image, (5, 5), 0)

    def crop_roi(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
        return image[y : y + h, x : x + w]

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def threshold(self, image: np.ndarray) -> np.ndarray:
        gray = self.to_grayscale(image)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
