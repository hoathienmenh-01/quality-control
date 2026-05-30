# 🏭 KẾ HOẠCH TRIỂN KHAI: QUALITY CONTROL SYSTEM
## Hệ Thống Kiểm Tra Chất Lượng Bằng Computer Vision

**Ngày lập:** 31/05/2026  
**Trạng thái:** Sẵn sàng triển khai  
**Tổng thời gian:** 8 tuần (2 tháng)  
**Tech stack:** Python, FastAPI, OpenCV, React, PostgreSQL, Docker

---

## 📖 MỤC LỤC

1. [Tổng quan kế hoạch](#1-tổng-quan-kế-hoạch)
2. [Phase 1: Foundation (Tuần 1-2)](#2-phase-1-foundation-tuần-1-2)
3. [Phase 2: Core Engine (Tuần 3-4)](#3-phase-2-core-engine-tuần-3-4)
4. [Phase 3: Backend API (Tuần 5)](#4-phase-3-backend-api-tuần-5)
5. [Phase 4: Frontend Dashboard (Tuần 6)](#5-phase-4-frontend-dashboard-tuần-6)
6. [Phase 5: Export & Alerts (Tuần 7)](#6-phase-5-export--alerts-tuần-7)
7. [Phase 6: Testing & Polish (Tuần 8)](#7-phase-6-testing--polish-tuần-8)
8. [Cấu trúc thư mục](#8-cấu-trúc-thư-mục)
9. [Database Schema](#9-database-schema)
10. [API Endpoints](#10-api-endpoints)
11. [Docker & Deployment](#11-docker--deployment)
12. [Testing plan](#12-testing-plan)
13. [Thống kê công việc](#13-thống-kê-công-việc)

---

## 1. TỔNG QUAN KẾ HOẠCH

### Mục tiêu
Xây dựng hệ thống kiểm tra chất lượng sản phẩm điện tử bằng Computer Vision (không dùng AI/ML), có khả năng:
- ✅ Phát hiện thiếu linh kiện
- ✅ Kiểm tra mã QR
- ✅ Kiểm tra tem Serial Number
- ✅ Kiểm tra vị trí anten
- ✅ Xuất báo cáo Excel/SQL
- ✅ Dashboard theo dõi thời gian thực

### Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| **Backend** | Python 3.12, FastAPI, Celery |
| **CV Engine** | OpenCV, pyzbar, EasyOCR |
| **Database** | PostgreSQL 15, Redis 7 |
| **Frontend** | React 18, Tailwind CSS, Recharts |
| **Infrastructure** | Docker, Docker Compose, Nginx |
| **Export** | Pandas, openpyxl |
| **Alerts** | Telegram Bot API |

### Timeline tổng quan

```
Tuần 1-2: Foundation        ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  25%
Tuần 3-4: Core Engine       ░░░░░░░░░░██████████░░░░░░░░░░░░░░░░░░  50%
Tuần 5:   Backend API       ░░░░░░░░░░░░░░░░░░░░██████░░░░░░░░░░░░  62%
Tuần 6:   Frontend          ░░░░░░░░░░░░░░░░░░░░░░░░░░██████░░░░░░  75%
Tuần 7:   Export & Alerts   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██████  87%
Tuần 8:   Testing & Polish  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██ 100%
```

---

## 2. PHASE 1: FOUNDATION (Tuần 1-2)

### Tuần 1: Project Setup & Database

#### Task 1.1: Khởi tạo dự án
```
📂 quality-control/
├── api/                    # FastAPI backend
├── core/                   # CV engine, detection
├── frontend/               # React frontend
├── tests/                  # Test suite
├── migrations/             # Alembic migrations
├── scripts/                # Utility scripts
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── .env.example
```

**Chi tiết:**
- [ ] Khởi tạo Git repository
- [ ] Setup Python virtual environment
- [ ] Cài đặt dependencies (FastAPI, OpenCV, psycopg2, etc.)
- [ ] Cấu hình Alembic migrations
- [ ] Tạo `.env.example`
- [ ] Setup Docker cơ bản

**Dependencies:**
```
fastapi==0.110.0
uvicorn==0.29.0
sqlalchemy==2.0.28
alembic==1.13.1
psycopg2-binary==2.9.9
redis==5.0.3
celery==5.3.6
opencv-python==4.9.0.80
pyzbar==0.1.9
easyocr==1.7.1
pandas==2.2.1
openpyxl==3.1.2
python-telegram-bot==21.0
python-dotenv==1.0.1
python-multipart==0.0.9
```

#### Task 1.2: Database Schema
**Thời gian:** 2 ngày

- [ ] Tạo bảng `product_templates` (template sản phẩm)
- [ ] Tạo bảng `inspections` (kết quả kiểm tra)
- [ ] Tạo bảng `defect_summary` (thống kê lỗi)
- [ ] Tạo bảng `alerts` (cảnh báo)
- [ ] Tạo bảng `users` (người dùng)
- [ ] Tạo indexes cho performance
- [ ] Seed data mẫu

**SQL Schema:**

```sql
-- Bảng template sản phẩm
CREATE TABLE product_templates (
    id SERIAL PRIMARY KEY,
    product_type VARCHAR(100) NOT NULL UNIQUE,
    product_name VARCHAR(255),
    description TEXT,
    required_components JSONB NOT NULL,
    component_positions JSONB,
    antenna_position JSONB,
    sn_format VARCHAR(200),
    qr_format VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bảng kết quả kiểm tra
CREATE TABLE inspections (
    id SERIAL PRIMARY KEY,
    product_serial VARCHAR(100) NOT NULL,
    product_type VARCHAR(100),
    batch_number VARCHAR(50),
    station_id VARCHAR(50) NOT NULL,
    inspection_time TIMESTAMP DEFAULT NOW(),
    overall_result VARCHAR(10) NOT NULL,
    missing_components JSONB,
    detected_components JSONB,
    qr_result VARCHAR(20),
    qr_content TEXT,
    qr_error_detail VARCHAR(255),
    sn_result VARCHAR(20),
    sn_content TEXT,
    sn_error_detail VARCHAR(255),
    antenna_result VARCHAR(20),
    antenna_detected_position JSONB,
    antenna_error_detail VARCHAR(255),
    image_path VARCHAR(500),
    annotated_image_path VARCHAR(500),
    inference_time_ms FLOAT,
    inspector_type VARCHAR(20) DEFAULT 'cv',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_inspections_serial ON inspections(product_serial);
CREATE INDEX idx_inspections_time ON inspections(inspection_time);
CREATE INDEX idx_inspections_result ON inspections(overall_result);
CREATE INDEX idx_inspections_station ON inspections(station_id);

-- Bảng thống kê lỗi
CREATE TABLE defect_summary (
    id SERIAL PRIMARY KEY,
    summary_date DATE NOT NULL,
    station_id VARCHAR(50),
    total_inspected INT DEFAULT 0,
    total_passed INT DEFAULT 0,
    total_failed INT DEFAULT 0,
    pass_rate FLOAT,
    missing_component_count INT DEFAULT 0,
    qr_error_count INT DEFAULT 0,
    sn_error_count INT DEFAULT 0,
    antenna_error_count INT DEFAULT 0,
    top_missing_components JSONB,
    top_qr_errors JSONB,
    top_sn_errors JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(summary_date, station_id)
);

-- Bảng cảnh báo
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    station_id VARCHAR(50),
    product_type VARCHAR(100),
    batch_number VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bảng người dùng
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'operator',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Task 1.3: SQLAlchemy Models
**Thời gian:** 1 ngày

- [ ] Tạo model `ProductTemplate`
- [ ] Tạo model `Inspection`
- [ ] Tạo model `DefectSummary`
- [ ] Tạo model `Alert`
- [ ] Tạo model `User`
- [ ] Tạo relationship giữa các model

---

### Tuần 2: Camera Integration & Image Processing

#### Task 2.1: Camera Module
**Thời gian:** 3 ngày

- [ ] Tạo class `CameraManager` quản lý camera
- [ ] Hỗ trợ USB camera (OpenCV VideoCapture)
- [ ] Hỗ trợ IP camera (RTSP stream)
- [ ] Cấu hình resolution, FPS, exposure
- [ ] Capture ảnh theo trigger (GPIO/web request)
- [ ] Lưu ảnh vào disk với timestamp

**Code structure:**
```python
# core/camera.py
class CameraManager:
    def __init__(self, camera_id=0, resolution=(1920, 1080)):
        self.camera_id = camera_id
        self.resolution = resolution
        self.cap = None
    
    def connect(self):
        """Kết nối camera"""
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
    
    def capture(self) -> np.ndarray:
        """Chụp 1 ảnh"""
        ret, frame = self.cap.read()
        if not ret:
            raise CameraError("Cannot capture frame")
        return frame
    
    def capture_to_file(self, path: str) -> str:
        """Chụp ảnh và lưu file"""
        frame = self.capture()
        cv2.imwrite(path, frame)
        return path
    
    def disconnect(self):
        """Ngắt kết nối"""
        if self.cap:
            self.cap.release()
```

#### Task 2.2: Image Processing Module
**Thời gian:** 2 ngày

- [ ] Tạo class `ImageProcessor` xử lý ảnh
- [ ] Resize ảnh về kích thước chuẩn
- [ ] Normalize ánh sáng (histogram equalization)
- [ ] Crop vùng quan tâm (ROI)
- [ ] Chuyển đổi màu sắc (BGR → HSV, Grayscale)
- [ ] Khử nhiễu (Gaussian blur, median blur)

**Code structure:**
```python
# core/image_processor.py
class ImageProcessor:
    def __init__(self, target_size=(1920, 1080)):
        self.target_size = target_size
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Xử lý ảnh trước khi phân tích"""
        # Resize
        image = self.resize(image)
        # Normalize brightness
        image = self.normalize_brightness(image)
        # Denoise
        image = self.denoise(image)
        return image
    
    def resize(self, image: np.ndarray) -> np.ndarray:
        return cv2.resize(image, self.target_size)
    
    def normalize_brightness(self, image: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:,:,2] = cv2.equalizeHist(hsv[:,:,2])
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    def denoise(self, image: np.ndarray) -> np.ndarray:
        return cv2.GaussianBlur(image, (5, 5), 0)
    
    def crop_roi(self, image: np.ndarray, x, y, w, h) -> np.ndarray:
        return image[y:y+h, x:x+w]
```

---

## 3. PHASE 2: CORE ENGINE (Tuần 3-4)

### Tuần 3: Detection Modules

#### Task 3.1: Component Detector (Kiểm tra linh kiện)
**Thời gian:** 3 ngày

- [ ] Tạo class `ComponentDetector`
- [ ] Template matching (so sánh với ảnh mẫu)
- [ ] Contour detection (đếm linh kiện)
- [ ] So sánh với template chuẩn
- [ ] Trả về danh sách linh kiện thiếu

**Cách hoạt động:**
```
1. Load ảnh sản phẩm
2. Chuyển grayscale
3. Tìm contours (hình dạng linh kiện)
4. Đếm số contours tìm được
5. So sánh với template (số lượng, vị trí)
6. Thiếu contour nào = thiếu linh kiện
```

**Code structure:**
```python
# core/component_detector.py
class ComponentDetector:
    def __init__(self):
        self.templates = {}
    
    def load_template(self, product_type: str, template_path: str):
        """Load template ảnh chuẩn cho sản phẩm"""
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        self.templates[product_type] = template
    
    def detect(self, image: np.ndarray, product_type: str) -> dict:
        """Phát hiện linh kiện trong ảnh"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template = self.templates.get(product_type)
        
        if template is None:
            raise ValueError(f"No template for product type: {product_type}")
        
        # Tìm contours trong ảnh
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Đếm linh kiện theo kích thước
        components = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter noise
                x, y, w, h = cv2.boundingRect(contour)
                components.append({"x": x, "y": y, "w": w, "h": h, "area": area})
        
        # So sánh với template
        required = self.get_required_components(product_type)
        detected = self.match_components(components, required)
        missing = self.find_missing(required, detected)
        
        return {
            "detected": detected,
            "missing": missing,
            "is_pass": len(missing) == 0
        }
```

#### Task 3.2: QR Checker (Kiểm tra mã QR)
**Thời gian:** 2 ngày

- [ ] Tạo class `QRChecker`
- [ ] Đọc QR bằng pyzbar
- [ ] Validate format bằng regex
- [ ] Check duplicate trong database
- [ ] Check khớp với batch

**Code structure:**
```python
# core/qr_checker.py
from pyzbar.pyzbar import decode
import re

class QRChecker:
    def __init__(self, db_session):
        self.db = db_session
    
    def check(self, image: np.ndarray, expected_format: str = None, 
              batch_number: str = None) -> dict:
        """Kiểm tra mã QR"""
        # Đọc QR
        decoded = decode(image)
        
        if not decoded:
            return {
                "result": "NOT_FOUND",
                "content": None,
                "error": "QR not found in image"
            }
        
        qr_content = decoded[0].data.decode('utf-8')
        
        # Validate format
        if expected_format and not re.match(expected_format, qr_content):
            return {
                "result": "FAIL",
                "content": qr_content,
                "error": f"Format mismatch: expected {expected_format}"
            }
        
        # Check duplicate
        if self.db.exists_qr(qr_content):
            return {
                "result": "FAIL",
                "content": qr_content,
                "error": "Duplicate QR (tem dán nhầm)"
            }
        
        # Check batch
        if batch_number and not qr_content.endswith(batch_number):
            return {
                "result": "FAIL",
                "content": qr_content,
                "error": f"Batch mismatch: expected {batch_number}"
            }
        
        return {
            "result": "PASS",
            "content": qr_content,
            "error": None
        }
```

---

### Tuần 4: SN Checker & Anten Checker

#### Task 4.1: SN Checker (Kiểm tra tem SN)
**Thời gian:** 3 ngày

- [ ] Tạo class `SNChecker`
- [ ] Đọc SN bằng EasyOCR
- [ ] Validate format bằng regex
- [ ] Check duplicate trong database
- [ ] Xử lý ảnh tem (crop, enhance trước khi OCR)

**Code structure:**
```python
# core/sn_checker.py
import easyocr
import re

class SNChecker:
    def __init__(self, db_session, languages=['en']):
        self.db = db_session
        self.reader = easyocr.Reader(languages)
    
    def check(self, image: np.ndarray, sn_region: dict, 
              expected_format: str = None) -> dict:
        """Kiểm tra tem Serial Number"""
        # Crop vùng tem SN
        x, y, w, h = sn_region['x'], sn_region['y'], sn_region['w'], sn_region['h']
        sn_image = image[y:y+h, x:x+w]
        
        # Enhance ảnh tem
        sn_image = self.enhance_sn_image(sn_image)
        
        # OCR đọc text
        results = self.reader.readtext(sn_image)
        
        if not results:
            return {
                "result": "NOT_READABLE",
                "content": None,
                "error": "Cannot read SN (tem mờ/rách)"
            }
        
        sn_text = results[0][1].strip()
        confidence = results[0][2]
        
        # Check confidence
        if confidence < 0.5:
            return {
                "result": "NOT_READABLE",
                "content": sn_text,
                "error": f"Low confidence: {confidence:.2f}"
            }
        
        # Validate format
        if expected_format and not re.match(expected_format, sn_text):
            return {
                "result": "FAIL",
                "content": sn_text,
                "error": f"Format mismatch: expected {expected_format}"
            }
        
        # Check duplicate
        if self.db.exists_sn(sn_text):
            return {
                "result": "FAIL",
                "content": sn_text,
                "error": "Duplicate SN"
            }
        
        return {
            "result": "PASS",
            "content": sn_text,
            "error": None
        }
    
    def enhance_sn_image(self, image: np.ndarray) -> np.ndarray:
        """Cải thiện ảnh tem SN trước khi OCR"""
        # Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Threshold để tăng contrast
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
```

#### Task 4.2: Anten Checker (Kiểm tra anten)
**Thời gian:** 2 ngày

- [ ] Tạo class `AntenChecker`
- [ ] Phát hiện anten theo màu sắc/shape
- [ ] Tính vị trí (x, y) của anten
- [ ] Tính góc gắn anten
- [ ] So sánh với vị trí chuẩn trong template

**Code structure:**
```python
# core/anten_checker.py
class AntenChecker:
    def __init__(self):
        pass
    
    def check(self, image: np.ndarray, anten_region: dict,
              expected_position: dict, tolerance: int = 10,
              angle_tolerance: int = 5) -> dict:
        """Kiểm tra vị trí anten"""
        # Crop vùng anten
        x, y, w, h = anten_region['x'], anten_region['y'], anten_region['w'], anten_region['h']
        anten_image = image[y:y+h, x:x+w]
        
        # Tìm anten theo màu sắc
        detected = self.detect_anten_by_color(anten_image)
        
        if not detected:
            return {
                "result": "NOT_FOUND",
                "detected_position": None,
                "error": "Anten not found"
            }
        
        # Tính vị trí thực tế (gốc tọa độ ảnh gốc)
        real_x = x + detected['x']
        real_y = y + detected['y']
        detected_angle = detected.get('angle', 0)
        
        # So sánh với vị trí chuẩn
        dx = abs(real_x - expected_position['x'])
        dy = abs(real_y - expected_position['y'])
        d_angle = abs(detected_angle - expected_position.get('angle', 0))
        
        detected_pos = {"x": real_x, "y": real_y, "angle": detected_angle}
        
        if dx > tolerance or dy > tolerance:
            return {
                "result": "FAIL",
                "detected_position": detected_pos,
                "error": f"Position offset: dx={dx}, dy={dy}"
            }
        
        if d_angle > angle_tolerance:
            return {
                "result": "FAIL",
                "detected_position": detected_pos,
                "error": f"Angle offset: {d_angle}°"
            }
        
        return {
            "result": "PASS",
            "detected_position": detected_pos,
            "error": None
        }
    
    def detect_anten_by_color(self, image: np.ndarray) -> dict:
        """Phát hiện anten theo màu sắc"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Mask màu đen (anten thường màu đen)
        lower = np.array([0, 0, 0])
        upper = np.array([180, 255, 50])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Tìm contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Lấy contour lớn nhất
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        
        # Tính góc (dựa vào bounding box)
        angle = self.calculate_angle(largest)
        
        return {"x": x, "y": y, "w": w, "h": h, "angle": angle}
```

#### Task 4.3: Inspection Pipeline (Tổng hợp)
**Thời gian:** 2 ngày

- [ ] Tạo class `InspectionPipeline` kết hợp tất cả detectors
- [ ] Chạy tuần tự: Component → QR → SN → Anten
- [ ] Tổng hợp kết quả PASS/FAIL
- [ ] Lưu kết quả vào database
- [ ] Lưu ảnh kết quả (annotate)

**Code structure:**
```python
# core/pipeline.py
class InspectionPipeline:
    def __init__(self, db_session):
        self.db = db_session
        self.component_detector = ComponentDetector()
        self.qr_checker = QRChecker(db_session)
        self.sn_checker = SNChecker(db_session)
        self.anten_checker = AntenChecker()
        self.image_processor = ImageProcessor()
    
    def inspect(self, image: np.ndarray, product_type: str,
                station_id: str, batch_number: str = None) -> dict:
        """Chạy toàn bộ kiểm tra cho 1 sản phẩm"""
        import time
        start_time = time.time()
        
        # Preprocess ảnh
        processed = self.image_processor.preprocess(image)
        
        # Load template
        template = self.db.get_template(product_type)
        
        # 1. Kiểm tra linh kiện
        component_result = self.component_detector.detect(processed, product_type)
        
        # 2. Kiểm tra QR
        qr_region = template.get('qr_region', {})
        qr_result = self.qr_checker.check(
            self.image_processor.crop_roi(processed, **qr_region),
            expected_format=template.get('qr_format'),
            batch_number=batch_number
        )
        
        # 3. Kiểm tra SN
        sn_region = template.get('sn_region', {})
        sn_result = self.sn_checker.check(
            processed,
            sn_region=sn_region,
            expected_format=template.get('sn_format')
        )
        
        # 4. Kiểm tra Anten
        anten_region = template.get('anten_region', {})
        anten_result = self.anten_checker.check(
            processed,
            anten_region=anten_region,
            expected_position=template.get('antenna_position')
        )
        
        # Tổng hợp kết quả
        overall = "PASS"
        if (not component_result['is_pass'] or 
            qr_result['result'] != 'PASS' or
            sn_result['result'] != 'PASS' or
            anten_result['result'] != 'PASS'):
            overall = "FAIL"
        
        inference_time = (time.time() - start_time) * 1000  # ms
        
        # Tạo kết quả
        result = {
            "overall_result": overall,
            "product_type": product_type,
            "station_id": station_id,
            "batch_number": batch_number,
            "missing_components": component_result['missing'],
            "detected_components": component_result['detected'],
            "qr_result": qr_result['result'],
            "qr_content": qr_result['content'],
            "qr_error_detail": qr_result['error'],
            "sn_result": sn_result['result'],
            "sn_content": sn_result['content'],
            "sn_error_detail": sn_result['error'],
            "antenna_result": anten_result['result'],
            "antenna_detected_position": anten_result['detected_position'],
            "antenna_error_detail": anten_result['error'],
            "inference_time_ms": round(inference_time, 2)
        }
        
        # Lưu vào DB
        self.save_inspection(result)
        
        # Lưu ảnh kết quả
        annotated_path = self.save_annotated_image(image, result)
        result['annotated_image_path'] = annotated_path
        
        return result
```

---

## 4. PHASE 3: BACKEND API (Tuần 5)

### Task 5.1: FastAPI Application Setup
**Thời gian:** 1 ngày

- [ ] Tạo FastAPI app chính
- [ ] Cấu hình CORS, middleware
- [ ] Cấu hình database connection
- [ ] Cấu hình Redis connection
- [ ] Setup error handling

### Task 5.2: API Endpoints
**Thời gian:** 4 ngày

#### Auth Endpoints
```
POST   /api/v1/auth/login           # Đăng nhập
POST   /api/v1/auth/register        # Đăng ký
GET    /api/v1/auth/me              # Thông tin user hiện tại
```

#### Inspection Endpoints
```
GET    /api/v1/inspections           # Danh sách kiểm tra (phân trang)
GET    /api/v1/inspections/{id}      # Chi tiết 1 lần kiểm tra
POST   /api/v1/inspections           # Tạo kết quả kiểm tra mới
GET    /api/v1/inspections/stats     # Thống kê tổng quan
```

#### Template Endpoints
```
GET    /api/v1/templates             # Danh sách template
POST   /api/v1/templates             # Tạo template mới
PUT    /api/v1/templates/{id}        # Cập nhật template
DELETE /api/v1/templates/{id}        # Xóa template
```

#### Export Endpoints
```
GET    /api/v1/export/excel          # Export Excel
GET    /api/v1/export/csv            # Export CSV
GET    /api/v1/export/sql            # Export SQL dump
```

#### Defect Endpoints
```
GET    /api/v1/defects/summary       # Thống kê lỗi theo ngày
GET    /api/v1/defects/trend         # Xu hướng lỗi
GET    /api/v1/defects/top           # Top lỗi phổ biến
```

#### Alert Endpoints
```
GET    /api/v1/alerts                # Danh sách cảnh báo
PUT    /api/v1/alerts/{id}/read      # Đánh dấu đã đọc
PUT    /api/v1/alerts/{id}/resolve   # Đánh dấu đã giải quyết
```

#### Dashboard Endpoints
```
GET    /api/v1/dashboard/stats       # Thống kê dashboard
GET    /api/v1/dashboard/realtime    # Dữ liệu thời gian thực
```

#### Camera Endpoints
```
POST   /api/v1/camera/capture        # Chụp ảnh
GET    /api/v1/camera/status         # Trạng thái camera
POST   /api/v1/camera/connect        # Kết nối camera
```

---

## 5. PHASE 4: FRONTEND DASHBOARD (Tuần 6)

### Task 6.1: React App Setup
**Thời gian:** 1 ngày

- [ ] Khởi tạo React app với Vite
- [ ] Cấu hình Tailwind CSS
- [ ] Setup React Router
- [ ] Setup Zustand state management
- [ ] Setup Axios API client

### Task 6.2: Components & Pages
**Thời gian:** 4 ngày

#### Components
- [ ] `Layout.jsx` — Layout chính (sidebar + navbar)
- [ ] `Navbar.jsx` — Thanh điều hướng
- [ ] `Sidebar.jsx` — Menu bên trái
- [ ] `LoadingSpinner.jsx` — Loading state
- [ ] `StatusBadge.jsx` — PASS/FAIL badge
- [ ] `DefectChart.jsx` — Biểu đồ lỗi
- [ ] `TrendChart.jsx` — Biểu đồ xu hướng
- [ ] `InspectionCard.jsx` — Card kết quả kiểm tra

#### Pages
- [ ] `LoginPage.jsx` — Đăng nhập
- [ ] `DashboardPage.jsx` — Tổng quan
- [ ] `InspectionsPage.jsx` — Danh sách kiểm tra
- [ ] `InspectionDetailPage.jsx` — Chi tiết kiểm tra
- [ ] `TemplatesPage.jsx` — Quản lý template
- [ ] `ReportsPage.jsx` — Báo cáo & Export
- [ ] `AlertsPage.jsx` — Cảnh báo
- [ ] `SettingsPage.jsx` — Cài đặt
- [ ] `CameraPage.jsx` — Quản lý camera

#### Dashboard Layout
```
┌─────────────────────────────────────────────────────────────┐
│  🏭 Quality Control                     [🔔] [👤] [⚙️]     │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│ 📊 Overview     Tổng quan hôm nay                          │
│ 📋 Inspections  ┌──────┐┌──────┐┌──────┐┌──────┐          │
│ 📝 Templates    │1,250 ││1,180 ││  70  ││ 5.6% │          │
│ 📈 Reports      │Check ││PASS  ││FAIL  ││Rate  │          │
│ 🔔 Alerts       └──────┘└──────┘└──────┘└──────┘          │
│ 📷 Camera                                                      │
│ ⚙️ Settings     Xu hướng lỗi (30 ngày)                      │
│                ┌──────────────────────────────────┐         │
│                │    ╭──╮      ╭╮                  │         │
│                │  ╭─╯  ╰──╮╭─╯╰╮                 │         │
│                │──╯       ╰╯   ╰──────           │         │
│                └──────────────────────────────────┘         │
│                                                              │
│                Top lỗi hôm nay                               │
│                ┌──────────────────────────────────┐         │
│                │ Thiếu linh kiện │████████│ 50%   │         │
│                │ Sai QR          │████    │ 26%   │         │
│                │ Lệch anten      │███     │ 17%   │         │
│                │ Sai SN          │█       │  7%   │         │
│                └──────────────────────────────────┘         │
│                                                              │
│                [📷 Capture] [📥 Export] [🔄 Refresh]         │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 6. PHASE 5: EXPORT & ALERTS (Tuần 7)

### Task 6.1: Excel Export
**Thời gian:** 2 ngày

- [ ] Export chi tiết kiểm tra (1 sheet)
- [ ] Export thống kê theo ngày (1 sheet)
- [ ] Export thống kê theo trạm (1 sheet)
- [ ] Export top lỗi (1 sheet)
- [ ] Export thống kê theo batch (1 sheet)
- [ ] Format Excel đẹp (header, colors, borders)

### Task 6.2: CSV & SQL Export
**Thời gian:** 1 ngày

- [ ] Export CSV (đơn giản, dùng Pandas)
- [ ] Export SQL dump (INSERT statements)

### Task 6.3: Telegram Alerts
**Thời gian:** 2 ngày

- [ ] Tạo Telegram Bot
- [ ] Gửi alert khi tỷ lệ lỗi cao
- [ ] Gửi alert khi phát hiện lỗi mới
- [ ] Cấu hình threshold (ngưỡng cảnh báo)

**Alert types:**
```
HIGH_DEFECT_RATE    — Tỷ lệ lỗi > 10%
MISSING_COMPONENT   — Thiếu linh kiện
QR_ERROR            — Lỗi QR
SN_ERROR            — Lỗi SN
ANTENNA_ERROR       — Lỗi anten
CAMERA_DISCONNECTED — Mất kết nối camera
```

---

## 7. PHASE 6: TESTING & POLISH (Tuần 8)

### Task 7.1: Unit Tests
**Thời gian:** 2 ngày

- [ ] Test `ComponentDetector`
- [ ] Test `QRChecker`
- [ ] Test `SNChecker`
- [ ] Test `AntenChecker`
- [ ] Test `InspectionPipeline`
- [ ] Test API endpoints
- [ ] Test Excel/CSV export

### Task 7.2: Integration Tests
**Thời gian:** 1 ngày

- [ ] Test end-to-end flow
- [ ] Test camera → detection → DB → export
- [ ] Test multiple inspections

### Task 7.3: Performance Tests
**Thời gian:** 1 ngày

- [ ] Benchmark detection speed
- [ ] Test với nhiều ảnh cùng lúc
- [ ] Optimize nếu cần

### Task 7.4: Documentation
**Thời gian:** 1 ngày

- [ ] README.md tiếng Việt
- [ ] API documentation (Swagger)
- [ ] User guide
- [ ] Deployment guide

---

## 8. CẤU TRÚC THƯ MỤC

```
quality-control/
├── api/                            # FastAPI backend
│   ├── __init__.py
│   ├── app.py                      # App chính
│   ├── dependencies.py             # Dependencies injection
│   ├── auth.py                     # Authentication
│   └── routers/
│       ├── __init__.py
│       ├── auth.py                 # Auth endpoints
│       ├── inspections.py          # Inspection endpoints
│       ├── templates.py            # Template endpoints
│       ├── export.py               # Export endpoints
│       ├── defects.py              # Defect endpoints
│       ├── alerts.py               # Alert endpoints
│       ├── dashboard.py            # Dashboard endpoints
│       └── camera.py               # Camera endpoints
│
├── core/                           # CV Engine
│   ├── __init__.py
│   ├── camera.py                   # Camera management
│   ├── image_processor.py          # Image preprocessing
│   ├── component_detector.py       # Component detection
│   ├── qr_checker.py               # QR validation
│   ├── sn_checker.py               # SN validation
│   ├── anten_checker.py            # Anten detection
│   └── pipeline.py                 # Inspection pipeline
│
├── models/                         # SQLAlchemy models
│   ├── __init__.py
│   ├── base.py                     # Base model
│   ├── template.py                 # ProductTemplate
│   ├── inspection.py               # Inspection
│   ├── defect_summary.py           # DefectSummary
│   ├── alert.py                    # Alert
│   └── user.py                     # User
│
├── services/                       # Business logic
│   ├── __init__.py
│   ├── inspection_service.py       # Inspection logic
│   ├── export_service.py           # Export logic
│   ├── alert_service.py            # Alert logic
│   └── stats_service.py            # Statistics
│
├── frontend/                       # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── StatusBadge.jsx
│   │   │   ├── DefectChart.jsx
│   │   │   ├── TrendChart.jsx
│   │   │   └── InspectionCard.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── InspectionsPage.jsx
│   │   │   ├── InspectionDetailPage.jsx
│   │   │   ├── TemplatesPage.jsx
│   │   │   ├── ReportsPage.jsx
│   │   │   ├── AlertsPage.jsx
│   │   │   ├── CameraPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── authStore.js
│   │   ├── utils/
│   │   │   └── helpers.js
│   │   ├── styles/
│   │   │   └── index.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── tests/                          # Test suite
│   ├── unit/
│   │   ├── test_component_detector.py
│   │   ├── test_qr_checker.py
│   │   ├── test_sn_checker.py
│   │   ├── test_anten_checker.py
│   │   └── test_pipeline.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_export.py
│   └── performance/
│       └── test_benchmark.py
│
├── scripts/                        # Utility scripts
│   ├── seed_data.py                # Seed database
│   ├── capture_samples.py          # Chụp ảnh mẫu
│   └── generate_report.py          # Tạo báo cáo
│
├── migrations/                     # Alembic
│   └── versions/
│
├── templates/                      # Ảnh template mẫu
│   ├── PCB-A001/
│   │   ├── component_template.png
│   │   ├── qr_region.json
│   │   ├── sn_region.json
│   │   └── anten_region.json
│   └── PCB-B002/
│       └── ...
│
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.worker
├── requirements.txt
├── alembic.ini
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

---

## 9. DATABASE SCHEMA

### 9.1 Tables

| Table | Records (ước tính) | Purpose |
|-------|-------------------|---------|
| `product_templates` | 10-50 | Template sản phẩm |
| `inspections` | 1M+/năm | Kết quả kiểm tra |
| `defect_summary` | 365/năm | Thống kê theo ngày |
| `alerts` | 100-1000/tháng | Cảnh báo |
| `users` | 10-50 | Người dùng |

### 9.2 Index Strategy

```sql
-- Index cho inspections (bảng lớn nhất)
CREATE INDEX idx_inspections_serial ON inspections(product_serial);
CREATE INDEX idx_inspections_time ON inspections(inspection_time);
CREATE INDEX idx_inspections_result ON inspections(overall_result);
CREATE INDEX idx_inspections_station ON inspections(station_id);
CREATE INDEX idx_inspections_batch ON inspections(batch_number);
CREATE INDEX idx_inspections_type_time ON inspections(product_type, inspection_time);

-- Composite index cho queries phổ biến
CREATE INDEX idx_inspections_station_time ON inspections(station_id, inspection_time);
CREATE INDEX idx_inspections_result_time ON inspections(overall_result, inspection_time);
```

---

## 10. API ENDPOINTS

### 10.1 Authentication

```
POST /api/v1/auth/login
Body: { "email": "string", "password": "string" }
Response: { "access_token": "string", "token_type": "bearer" }

POST /api/v1/auth/register
Body: { "email": "string", "name": "string", "password": "string" }
Response: { "id": int, "email": "string", "name": "string" }

GET /api/v1/auth/me
Headers: Authorization: Bearer <token>
Response: { "id": int, "email": "string", "name": "string", "role": "string" }
```

### 10.2 Inspections

```
GET /api/v1/inspections?page=1&limit=50&date_from=2026-01-01&date_to=2026-12-31&result=FAIL&station=STATION-01
Response: {
  "items": [...],
  "total": 1000,
  "page": 1,
  "limit": 50
}

GET /api/v1/inspections/{id}
Response: { "id": 1, "product_serial": "SN-2026-A12345", ... }

POST /api/v1/inspections
Body: {
  "image": <file>,
  "product_type": "PCB-A001",
  "station_id": "STATION-01",
  "batch_number": "BATCH-001"
}
Response: { "id": 1, "overall_result": "PASS", ... }
```

### 10.3 Export

```
GET /api/v1/export/excel?date_from=2026-01-01&date_to=2026-12-31&station=STATION-01
Response: <Excel file download>

GET /api/v1/export/csv?date_from=2026-01-01&date_to=2026-12-31
Response: <CSV file download>

GET /api/v1/export/sql?date_from=2026-01-01&date_to=2026-12-31
Response: <SQL file download>
```

---

## 11. DOCKER & DEPLOYMENT

### 11.1 docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: qc_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: quality_control
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    command: uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
      - ./templates:/app/templates
      - ./captures:/app/captures
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://qc_user:${POSTGRES_PASSWORD}@postgres:5432/quality_control
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  worker:
    build: .
    command: celery -A core.celery_app:app worker --loglevel=info
    volumes:
      - .:/app
      - ./templates:/app/templates
      - ./captures:/app/captures
    environment:
      DATABASE_URL: postgresql://qc_user:${POSTGRES_PASSWORD}@postgres:5432/quality_control
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
      - frontend

volumes:
  postgres_data:
```

### 11.2 .env.example

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://qc_user:${POSTGRES_PASSWORD}@localhost:5432/quality_control

# Redis
REDIS_URL=redis://localhost:6379/0

# API
SECRET_KEY=your_secret_key
API_KEY=your_api_key

# Telegram Alerts
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Camera
CAMERA_ID=0
CAMERA_RESOLUTION_WIDTH=1920
CAMERA_RESOLUTION_HEIGHT=1080

# Thresholds
DEFECT_RATE_THRESHOLD=10.0
```

---

## 12. TESTING PLAN

### 12.1 Unit Tests

| Module | Tests | Priority |
|--------|-------|----------|
| `ComponentDetector` | 10 | Cao |
| `QRChecker` | 8 | Cao |
| `SNChecker` | 8 | Cao |
| `AntenChecker` | 8 | Cao |
| `InspectionPipeline` | 5 | Cao |
| `ImageProcessor` | 5 | Trung bình |
| `CameraManager` | 5 | Trung bình |
| API endpoints | 20 | Cao |
| Export functions | 5 | Trung bình |
| **Tổng** | **74** | |

### 12.2 Integration Tests

| Test | Mô tả |
|------|-------|
| Full inspection flow | Camera → Detect → DB → Export |
| Multiple inspections | 100 ảnh liên tiếp |
| Error handling | Camera mất kết nối, ảnh mờ |

### 12.3 Performance Benchmarks

| Metric | Target |
|--------|--------|
| Detection time | < 200ms |
| Throughput | > 5 sản phẩm/giây |
| Memory usage | < 500MB |
| CPU usage | < 50% (1 camera) |

---

## 13. THỐNG KÊ CÔNG VIỆC

### Tổng quan

| Phase | Tasks | Thời gian | Status |
|-------|-------|-----------|--------|
| Phase 1: Foundation | 5 | Tuần 1-2 | ⏳ |
| Phase 2: Core Engine | 5 | Tuần 3-4 | ⏳ |
| Phase 3: Backend API | 2 | Tuần 5 | ⏳ |
| Phase 4: Frontend | 2 | Tuần 6 | ⏳ |
| Phase 5: Export & Alerts | 3 | Tuần 7 | ⏳ |
| Phase 6: Testing | 4 | Tuần 8 | ⏳ |
| **Tổng** | **21 tasks** | **8 tuần** | |

### Ước tính code

| Component | Files | Lines (ước tính) |
|-----------|-------|------------------|
| Backend (API) | 15 | ~2,000 |
| Core (CV Engine) | 7 | ~1,500 |
| Models | 6 | ~500 |
| Services | 4 | ~800 |
| Frontend | 20 | ~3,000 |
| Tests | 10 | ~1,500 |
| Config/Docker | 5 | ~300 |
| Documentation | 3 | ~1,000 |
| **Tổng** | **70 files** | **~10,600 lines** |

---

**Kế hoạch được lập bởi:** AI Assistant  
**Ngày:** 31/05/2026  
**Trạng thái:** Sẵn sàng triển khai

---

*Quality Control System — Kiểm tra chất lượng thông minh, sản xuất hiệu quả.* 🏭
