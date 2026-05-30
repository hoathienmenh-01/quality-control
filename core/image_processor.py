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
        """Cân bằng sáng sử dụng CLAHE trên kênh V"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        hsv[:, :, 2] = clahe.apply(hsv[:, :, 2])
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

    # --- New CV methods ---

    def apply_clahe(self, image: np.ndarray, clip_limit: float = 2.0,
                    tile_grid_size: tuple = (8, 8)) -> np.ndarray:
        """Áp dụng CLAHE (Contrast Limited Adaptive Histogram Equalization)
        cho ảnh grayscale hoặc ảnh màu (trên kênh L/V)"""
        if len(image.shape) == 2:
            # Grayscale
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            return clahe.apply(image)
        else:
            # Color - apply on L channel of LAB
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tile_gridSize=tile_grid_size)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def adaptive_threshold(self, image: np.ndarray, block_size: int = 11,
                           c: int = 2, method: str = "gaussian") -> np.ndarray:
        """Áp dụng adaptive thresholding (Gaussian hoặc Mean)"""
        gray = self.to_grayscale(image) if len(image.shape) == 3 else image
        # block_size phải là số lẻ >= 3
        block_size = max(3, block_size | 1)
        if method == "gaussian":
            return cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, block_size, c
            )
        else:
            return cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY, block_size, c
            )

    def perspective_correction(self, image: np.ndarray,
                               src_points: np.ndarray,
                               dst_size: tuple = None) -> np.ndarray:
        """Chỉnh sửa phối cảnh từ 4 điểm nguồn"""
        src = np.float32(src_points)
        if dst_size is None:
            # Tự tính kích thước đầu ra
            w1 = np.linalg.norm(src[1] - src[0])
            w2 = np.linalg.norm(src[2] - src[3])
            h1 = np.linalg.norm(src[3] - src[0])
            h2 = np.linalg.norm(src[2] - src[1])
            dst_w = int(max(w1, w2))
            dst_h = int(max(h1, h2))
            dst_size = (dst_w, dst_h)

        dst = np.float32([
            [0, 0],
            [dst_size[0], 0],
            [dst_size[0], dst_size[1]],
            [0, dst_size[1]]
        ])
        matrix = cv2.getPerspectiveTransform(src, dst)
        return cv2.warpPerspective(image, matrix, dst_size)

    def auto_perspective_correction(self, image: np.ndarray) -> np.ndarray:
        """Tự động tìm giấy/tài liệu và chỉnh sửa phối cảnh"""
        gray = self.to_grayscale(image)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image

        largest = max(contours, key=cv2.contourArea)
        epsilon = 0.02 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)

        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            # Sắp xếp: top-left, top-right, bottom-right, bottom-left
            s = pts.sum(axis=1)
            diff = np.diff(pts, axis=1)
            ordered = np.array([
                pts[np.argmin(s)],
                pts[np.argmin(diff)],
                pts[np.argmax(s)],
                pts[np.argmax(diff)]
            ])
            return self.perspective_correction(image, ordered)
        return image

    def edge_detection_canny(self, image: np.ndarray,
                             low_threshold: int = 50,
                             high_threshold: int = 150) -> np.ndarray:
        """Phát hiện biên sử dụng Canny"""
        gray = self.to_grayscale(image) if len(image.shape) == 3 else image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        return cv2.Canny(blurred, low_threshold, high_threshold)

    def morphological_operation(self, image: np.ndarray, operation: str = "dilate",
                                kernel_size: int = 3, iterations: int = 1) -> np.ndarray:
        """Thao tác hình thái học: dilate, erode, open, close, gradient"""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        if operation == "dilate":
            return cv2.dilate(image, kernel, iterations=iterations)
        elif operation == "erode":
            return cv2.erode(image, kernel, iterations=iterations)
        elif operation == "open":
            return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
        elif operation == "close":
            return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        elif operation == "gradient":
            return cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel, iterations=iterations)
        else:
            raise ValueError(f"Unknown morphological operation: {operation}")

    def enhance_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Chuẩn bị ảnh cho OCR: CLAHE + adaptive threshold + morph close"""
        gray = self.to_grayscale(image) if len(image.shape) == 3 else image
        clahe = self.apply_clahe(gray)
        thresh = self.adaptive_threshold(clahe, block_size=15, c=4)
        # Morph close để lấp lỗ nhỏ
        closed = self.morphological_operation(thresh, "close", kernel_size=3, iterations=1)
        return closed
