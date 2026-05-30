# 📋 BÁO CÁO DỰ ÁN: AI QUALITY CONTROL
## Hệ Thống Kiểm Tra Chất Lượng Sản Phẩm Bằng AI

**Ngày lập:** 31/05/2026  
**Phiên bản:** 1.0  
**Trạng thái:** Ý tưởng & Lập kế hoạch

---

## 📖 MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Vấn đề & Giải pháp](#2-vấn-đề--giải-pháp)
3. [Phân tích chức năng chi tiết](#3-phân-chức-năng-chi-tiết)
4. [Kiến trúc hệ thống](#4-kiến-trúc-hệ-thống)
5. [Công nghệ sử dụng](#5-công-nghệ-sử-dụng)
6. [Cơ sở dữ liệu](#6-cơ-sở-dữ-liệu)
7. [API & Export](#7-api--export)
8. [Dashboard & Giao diện](#8-dashboard--giao-diện)
9. [Phân tích chi phí & ROI](#9-phân-tích-chi-phí--roi)
10. [Roadmap triển khai](#10-roadmap-triển-khai)
11. [Rủi ro & Giải pháp](#11-rủi-ro--giải-pháp)
12. [Kết luận](#12-kết-luận)

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1 Tên dự án
**AI Quality Control** — Hệ thống kiểm tra chất lượng sản phẩm điện tử bằng trí tuệ nhân tạo

### 1.2 Mô tả ngắn
Hệ thống sử dụng camera + AI để tự động kiểm tra chất lượng sản phẩm trên dây chuyền sản xuất, phát hiện:
- Thiếu linh kiện
- Sai mã QR
- Sai tem Serial Number (SN)
- Gắn lệch anten

Kết quả kiểm tra được lưu vào database, xuất báo cáo SQL/Excel, và hiển thị trên dashboard thời gian thực.

### 1.3 Đối tượng sử dụng
| Đối tượng | Mô tả |
|-----------|-------|
| **Nhà máy sản xuất điện tử** | Dây chuyền SMT, PCB assembly |
| **QC Manager** | Quản lý chất lượng sản xuất |
| **Operator** | Công nhân vận hành dây chuyền |
| **Ban giám đốc** | Xem báo cáo tổng quan |

### 1.4 Mục tiêu dự án
- ✅ Tự động hóa kiểm tra chất lượng (thay thế kiểm tra thủ công bằng mắt)
- ✅ Tăng tốc độ kiểm tra từ 100 sản phẩm/giờ lên 1.000+ sản phẩm/giờ
- ✅ Giảm tỷ lệ lỗi sót (từ ~5% xuống <0.1%)
- ✅ Lưu trữ lịch sử kiểm tra, xuất báo cáo SQL/Excel
- ✅ Dashboard thời gian thực, cảnh báo real-time

---

## 2. VẤN ĐỀ & GIẢI PHÁP

### 2.1 Vấn đề hiện tại

| Vấn đề | Mô tả | Tác động |
|--------|-------|----------|
| **Kiểm tra bằng mắt** | Công nhân nhìn sản phẩm, kiểm tra thủ công | Chậm, mỏi mắt, sai sót |
| **Tốc độ chậm** | ~100 sản phẩm/giờ | Nút thắt cổ chai sản xuất |
| **Tỷ lệ lỗi sót** | ~3-5% sản phẩm lỗi bị bỏ qua | Sản phẩm lỗi đến tay khách hàng |
| **Không lưu lịch sử** | Không có dữ liệu kiểm tra | Không phân tích xu hướng được |
| **Không cảnh báo** | Không biết khi nào tỷ lệ lỗi tăng | Phản ứng chậm |
| **Chi phí nhân sự** | Cần nhiều công nhân QC | Tăng chi phí sản xuất |

### 2.2 Giải pháp AI

| Vấn đề | Giải pháp AI | Kết quả mong đợi |
|--------|-------------|------------------|
| Kiểm tra bằng mắt | Camera + AI tự động kiểm tra | Không cần nhân sự |
| Tốc độ chậm | YOLOv8 inference <50ms/ảnh | 1.000+ sản phẩm/giờ |
| Tỷ lệ lỗi sót | AI không mỏi, không mất tập trung | <0.1% lỗi sót |
| Không lưu lịch sử | PostgreSQL lưu mọi kết quả | Phân tích xu hướng |
| Không cảnh báo | Alert real-time qua Telegram/Dashboard | Phản ứng ngay |
| Chi phí nhân sự | Giảm 70-80% nhân sự QC | Tiết kiệm chi phí |

---

## 3. PHÂN TÍCH CHỨC NĂNG CHI TIẾT

### 3.1 Kiểm tra thiếu linh kiện

**Mô tả:** Camera chụp ảnh sản phẩm (PCB board), AI phát hiện từng linh kiện và so sánh với template chuẩn.

**Luồng hoạt động:**
```
Camera chụp ảnh sản phẩm
        ↓
YOLOv8 phát hiện từng linh kiện (R1, R2, C1, C2, IC1, LED1, Socket, Anten...)
        ↓
So sánh với template chuẩn (danh sách linh kiện bắt buộc)
        ↓
Thiếu linh kiện nào → Ghi lỗi
```

**Ví dụ:**
```
Template chuẩn: [R1, R2, C1, C2, IC1, LED1, Socket1, Anten1]
Thực tế phát hiện: [R1, R2, C1, IC1, LED1, Socket1]
→ LỖI: Thiếu C2, Thiếu Anten1
```

**Chi tiết kỹ thuật:**
- **Model:** YOLOv8 (Ultralytics) — object detection
- **Input:** Ảnh sản phẩm từ camera công nghiệp (1920x1080)
- **Output:** Bounding box + label cho từng linh kiện
- **Accuracy mục tiêu:** >99.5%
- **Speed:** <50ms/ảnh trên GPU

**Template system:**
```python
# Template cho từng loại sản phẩm
product_templates = {
    "PCB-A001": {
        "required_components": ["R1", "R2", "R3", "C1", "C2", "C3", "IC1", "LED1", "Socket1", "Anten1"],
        "component_positions": {
            "R1": {"x": 100, "y": 150, "tolerance": 10},
            "R2": {"x": 200, "y": 150, "tolerance": 10},
            # ...
        }
    }
}
```

---

### 3.2 Kiểm tra mã QR

**Mô tả:** Camera chụp ảnh vùng QR, AI đọc và xác minh nội dung mã QR.

**Luồng hoạt động:**
```
Camera chụp ảnh vùng QR
        ↓
QR decoder (pyzbar / OpenCV) đọc nội dung
        ↓
Kiểm tra:
  1. QR có đọc được không? (in mờ, hư hỏng → FAIL)
  2. Nội dung đúng format không? (sai format → FAIL)
  3. QR có trùng với sản phẩm khác không? (tem dán nhầm → FAIL)
  4. QR có khớp với batch/serial không? (sai batch → FAIL)
```

**Các lỗi QR:**

| Lỗi | Mô tả | Cách phát hiện |
|-----|-------|----------------|
| QR không đọc được | In mờ, hư hỏng, thiếu | pyzbar trả về None |
| QR sai nội dung | Nội dung không đúng format | Regex check format |
| QR trùng | Tem dán nhầm, dán lại | Query DB check duplicate |
| QR sai batch | QR của batch khác | So sánh với batch hiện tại |

**Ví dụ:**
```
QR đọc được: "SN-2026-A12345-BATCH001"
Format check: ✅ Đúng format "SN-YYYY-XXXXX-BATCHXXX"
Duplicate check: ✅ Chưa tồn tại trong DB
Batch check: ✅ Khớp với batch hiện tại
→ PASS

QR đọc được: "SN-2026-A12345-BATCH001"
Duplicate check: ❌ Đã tồn tại (sản phẩm #1234)
→ FAIL: QR trùng! (tem dán nhầm)
```

---

### 3.3 Kiểm tra tem Serial Number (SN)

**Mô tả:** Camera chụp ảnh tem SN, AI đọc text bằng OCR và xác minh.

**Luồng hoạt động:**
```
Camera chụp ảnh tem SN
        ↓
OCR (EasyOCR / PaddleOCR) đọc text
        ↓
Kiểm tra:
  1. Tem có tồn tại không? (thiếu tem → FAIL)
  2. OCR đọc được không? (tem mờ, rách → FAIL)
  3. Format đúng không? (sai format → FAIL)
  4. SN có trùng không? (trùng → FAIL)
  5. SN có khớp với QR không? (không khớp → FAIL)
```

**Các lỗi SN:**

| Lỗi | Mô tả | Cách phát hiện |
|-----|-------|----------------|
| Thiếu tem | Không có tem SN | OCR trả về None |
| Tem mờ/rách | OCR không đọc được | Confidence < threshold |
| Sai format | Không đúng regex | Regex check |
| SN trùng | Tem dán nhầm | Query DB check duplicate |
| SN-QR mismatch | SN không khớp QR | So sánh SN vs QR content |

**Format validation:**
```python
import re

sn_formats = {
    "product-A": r"^SN-\d{4}-[A-Z]\d{5}$",      # SN-2026-A12345
    "product-B": r"^LOT\d{6}-\d{4}$",             # LOT001234-5678
    "product-C": r"^[A-Z]{2}\d{8}$",               # AB12345678
}

def validate_sn(sn, product_type):
    pattern = sn_formats.get(product_type)
    if not pattern:
        return False, "Unknown product type"
    if not re.match(pattern, sn):
        return False, f"SN format mismatch: expected {pattern}"
    return True, "OK"
```

---

### 3.4 Kiểm tra gắn anten

**Mô tả:** Camera chụp ảnh sản phẩm, AI phát hiện vị trí và hướng gắn anten.

**Luồng hoạt động:**
```
Camera chụp ảnh sản phẩm (góc nhìn từ trên)
        ↓
YOLOv8 phát hiện vị trí anten (bounding box)
        ↓
Tính toán:
  1. Anten có đủ không? (thiếu → FAIL)
  2. Vị trí đúng không? (sai vị trí → FAIL)
  3. Hướng gắn đúng không? (lệch góc → FAIL)
  4. Anten có bị lỏng không? (không khớp → FAIL)
```

**Kiểm tra vị trí & góc:**
```python
import math

def check_antenna(detected_position, template_position, tolerance=10, angle_tolerance=5):
    """
    Kiểm tra vị trí và góc gắn anten
    
    Args:
        detected_position: (x, y, angle) - vị trí phát hiện được
        template_position: (x, y, angle) - vị trí chuẩn
        tolerance: pixel tolerance cho vị trí
        angle_tolerance: độ tolerance cho góc
    
    Returns:
        (is_pass, details)
    """
    dx = abs(detected_position[0] - template_position[0])
    dy = abs(detected_position[1] - template_position[1])
    d_angle = abs(detected_position[2] - template_position[2])
    
    details = {
        "offset_x": dx,
        "offset_y": dy,
        "angle_diff": d_angle,
    }
    
    if dx > tolerance or dy > tolerance:
        return False, {**details, "reason": f"Vị trí lệch: dx={dx}, dy={dy}"}
    
    if d_angle > angle_tolerance:
        return False, {**details, "reason": f"Góc lệch: {d_angle}°"}
    
    return True, {**details, "reason": "OK"}
```

**Ví dụ:**
```
Template: Anten gắn tại (x=150, y=200), hướng 0° (thẳng đứng)
Thực tế: Anten gắn tại (x=165, y=195), hướng 15°
→ FAIL: Vị trí lệch dx=15px, Góc lệch 15° (cho phép ±5°)

Template: Anten gắn tại (x=150, y=200), hướng 0°
Thực tế: Anten gắn tại (x=152, y=198), hướng 2°
→ PASS: Vị trí OK, Góc OK
```

---

## 4. KIẾN TRÚC HỆ THỐNG

### 4.1 Sơ đồ tổng quan

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CAMERA SYSTEM                                  │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│    │ Camera 1 │  │ Camera 2 │  │ Camera 3 │  │ Camera N │         │
│    │ (USB/IP) │  │ (USB/IP) │  │ (USB/IP) │  │ (USB/IP) │         │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
└─────────┼──────────────┼──────────────┼──────────────┼──────────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EDGE COMPUTING LAYER                             │
│              (NVIDIA Jetson / Raspberry Pi / PC)                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 AI PROCESSING PIPELINE                       │   │
│  │                                                             │   │
│  │  1. Image Preprocessing (OpenCV)                            │   │
│  │     → Resize, normalize, enhance                            │   │
│  │                                                             │   │
│  │  2. Object Detection (YOLOv8)                               │   │
│  │     → Phát hiện: linh kiện, QR, tem SN, anten              │   │
│  │                                                             │   │
│  │  3. OCR (EasyOCR / PaddleOCR)                               │   │
│  │     → Đọc mã QR, serial number                              │   │
│  │                                                             │   │
│  │  4. Defect Classification                                   │   │
│  │     → Đúng/Sai: vị trí, hướng, thiếu linh kiện             │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                                │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   FastAPI    │  │   Celery     │  │  WebSocket   │             │
│  │   Backend    │  │   Workers    │  │   Server     │             │
│  │  (REST API)  │  │ (Background) │  │  (Real-time) │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                 │                 │                      │
│         ▼                 ▼                 ▼                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL Database                       │   │
│  │  - inspections (kết quả kiểm tra)                           │   │
│  │  - product_templates (template sản phẩm)                    │   │
│  │  - defect_summary (thống kê lỗi)                            │   │
│  │  - users (người dùng)                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                               │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   React      │  │   Telegram   │  │   Excel/SQL  │             │
│  │  Dashboard   │  │    Alert     │  │    Export    │             │
│  │  (Frontend)  │  │    Bot       │  │   Reports    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Chi tiết từng lớp

#### Lớp Camera System
| Thành phần | Mô tả | Chi phí ước tính |
|-----------|-------|------------------|
| Camera công nghiệp | Độ phân giải 1920x1080, 30fps | 2-5 triệu/chiếc |
| Đèn LED chiếu sáng | Ánh sáng đều, không phản chiếu | 500k-1 triệu/bộ |
| Giá đỡ camera | Cố định góc chụp | 200k-500k/chiếc |

#### Lớp Edge Computing
| Thành phần | Mô tả | Chi phí ước tính |
|-----------|-------|------------------|
| NVIDIA Jetson Nano | Chạy AI inference | 2-3 triệu/chiếc |
| HOẶC Raspberry Pi 4 | Chạy lightweight models | 1-2 triệu/chiếc |
| HOẶC PC có GPU | Chạy full models | 10-20 triệu/chiếc |

#### Lớp Application
| Thành phần | Mô tả | Chi phí ước tính |
|-----------|-------|------------------|
| FastAPI Backend | REST API, xử lý logic | Open source |
| Celery Workers | Xử lý background tasks | Open source |
| PostgreSQL | Database | Open source |
| Redis | Message queue, cache | Open source |

#### Lớp Presentation
| Thành phần | Mô tả | Chi phí ước tính |
|-----------|-------|------------------|
| React Dashboard | Giao diện web | Open source |
| Telegram Bot | Cảnh báo real-time | Miễn phí |
| Excel Export | Báo cáo | Open source |

---

## 5. CÔNG NGHỆ SỬ DỤNG

### 5.1 AI & Computer Vision

| Công cụ | Phiên bản | Mục đích | Lý do chọn |
|---------|-----------|----------|------------|
| **YOLOv8** | 8.x | Object Detection | Nhanh, chính xác, dễ train |
| **OpenCV** | 4.x | Image Processing | Thư viện CV phổ biến nhất |
| **EasyOCR** | 1.x | OCR (đọc text) | Hỗ trợ tiếng Việt, dễ dùng |
| **PaddleOCR** | 2.x | OCR (alternative) | Chính xác hơn cho tiếng Việt |
| **pyzbar** | 0.x | QR Code Decode | Nhanh, lightweight |
| **Pillow** | 10.x | Image manipulation | Xử lý ảnh cơ bản |

### 5.2 Backend & Database

| Công cụ | Phiên bản | Mục đích | Lý do chọn |
|---------|-----------|----------|------------|
| **Python** | 3.12+ | Ngôn ngữ chính | Hệ sinh thái AI/ML tốt nhất |
| **FastAPI** | 0.110+ | REST API | Nhanh, async, auto docs |
| **Celery** | 5.x | Background tasks | Task queue phổ biến |
| **SQLAlchemy** | 2.x | ORM | ORM Python phổ biến nhất |
| **Alembic** | 1.x | Database migrations | Quản lý schema |
| **PostgreSQL** | 15+ | Database | Robust, JSON support |
| **Redis** | 7.x | Message queue, cache | Nhanh, lightweight |

### 5.3 Frontend

| Công cụ | Phiên bản | Mục đích | Lý do chọn |
|---------|-----------|----------|------------|
| **React** | 18.x | Frontend framework | Phổ biến, ecosystem lớn |
| **Tailwind CSS** | 3.x | Styling | Utility-first, nhanh |
| **Recharts** | 2.x | Charts | React chart library |
| **Lucide React** | 0.x | Icons | Icon đẹp, lightweight |
| **Zustand** | 4.x | State management | Nhẹ, đơn giản |

### 5.4 Infrastructure

| Công cụ | Phiên bản | Mục đích | Lý do chọn |
|---------|-----------|----------|------------|
| **Docker** | 24+ | Containerization | Đơn giản deployment |
| **Docker Compose** | 2.x | Multi-container | Quản lý nhiều services |
| **Nginx** | 1.x | Reverse proxy | SSL, load balancing |
| **Prometheus** | 2.x | Metrics collection | Monitoring |
| **Grafana** | 10.x | Metrics visualization | Dashboard |

---

## 6. CƠ SỞ DỮ LIỆU

### 6.1 Database Schema

```sql
-- =====================================================
-- BẢNG: product_templates (Template sản phẩm)
-- Mô tả: Định nghĩa linh kiện, vị trí chuẩn cho từng loại sản phẩm
-- =====================================================
CREATE TABLE product_templates (
    id SERIAL PRIMARY KEY,
    product_type VARCHAR(100) NOT NULL UNIQUE,     -- Mã loại sản phẩm (PCB-A001, PCB-B002...)
    product_name VARCHAR(255),                      -- Tên sản phẩm
    description TEXT,                               -- Mô tả
    
    -- Linh kiện bắt buộc (JSON array)
    required_components JSONB NOT NULL,
    -- Ví dụ: ["R1", "R2", "C1", "C2", "IC1", "LED1", "Socket1", "Anten1"]
    
    -- Vị trí linh kiện chuẩn (JSON object)
    component_positions JSONB,
    -- Ví dụ: {"R1": {"x": 100, "y": 150, "tolerance": 10}, ...}
    
    -- Vị trí anten chuẩn
    antenna_position JSONB,
    -- Ví dụ: {"x": 150, "y": 200, "angle": 0, "tolerance": 10, "angle_tolerance": 5}
    
    -- Format SN (regex)
    sn_format VARCHAR(200),
    -- Ví dụ: "^SN-\\d{4}-[A-Z]\\d{5}$"
    
    -- Format QR (regex)
    qr_format VARCHAR(200),
    -- Ví dụ: "^SN-\\d{4}-[A-Z]\\d{5}-BATCH\\d{3}$"
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- BẢNG: inspections (Kết quả kiểm tra)
-- Mô tả: Lưu kết quả kiểm tra từng sản phẩm
-- =====================================================
CREATE TABLE inspections (
    id SERIAL PRIMARY KEY,
    
    -- Thông tin sản phẩm
    product_serial VARCHAR(100) NOT NULL,           -- Serial number sản phẩm
    product_type VARCHAR(100),                       -- Loại sản phẩm (FK -> product_templates)
    batch_number VARCHAR(50),                        -- Số batch sản xuất
    station_id VARCHAR(50) NOT NULL,                 -- Mã trạm kiểm tra (STATION-01, STATION-02...)
    
    -- Thời gian
    inspection_time TIMESTAMP DEFAULT NOW(),
    
    -- Kết quả tổng quát
    overall_result VARCHAR(10) NOT NULL,             -- PASS / FAIL
    
    -- Chi tiết kiểm tra linh kiện
    missing_components JSONB,                        -- Danh sách linh kiện thiếu
    -- Ví dụ: ["C2", "Anten1"]
    
    detected_components JSONB,                       -- Danh sách linh kiện phát hiện được
    -- Ví dụ: ["R1", "R2", "C1", "IC1", "LED1", "Socket1"]
    
    -- Chi tiết kiểm tra QR
    qr_result VARCHAR(20),                           -- PASS / FAIL / NOT_FOUND / NOT_READABLE
    qr_content TEXT,                                 -- Nội dung QR đọc được
    qr_error_detail VARCHAR(255),                    -- Chi tiết lỗi QR
    
    -- Chi tiết kiểm tra SN
    sn_result VARCHAR(20),                           -- PASS / FAIL / NOT_FOUND / NOT_READABLE
    sn_content TEXT,                                 -- SN đọc được
    sn_error_detail VARCHAR(255),                    -- Chi tiết lỗi SN
    
    -- Chi tiết kiểm tra Anten
    antenna_result VARCHAR(20),                      -- PASS / FAIL / NOT_FOUND
    antenna_detected_position JSONB,                 -- Vị trí anten phát hiện được
    -- Ví dụ: {"x": 165, "y": 195, "angle": 15}
    antenna_error_detail VARCHAR(255),               -- Chi tiết lỗi anten
    
    -- Ảnh chụp
    image_path VARCHAR(500),                         -- Đường dẫn ảnh gốc
    annotated_image_path VARCHAR(500),               -- Đường dẫn ảnh đã annotate
    
    -- AI inference details
    inference_time_ms FLOAT,                         -- Thời gian suy luận (ms)
    model_version VARCHAR(50),                       -- Phiên bản model AI
    
    -- Metadata
    inspector_type VARCHAR(20) DEFAULT 'ai',         -- 'ai' / 'human'
    notes TEXT,                                      -- Ghi chú
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index cho queries nhanh
CREATE INDEX idx_inspections_serial ON inspections(product_serial);
CREATE INDEX idx_inspections_time ON inspections(inspection_time);
CREATE INDEX idx_inspections_result ON inspections(overall_result);
CREATE INDEX idx_inspections_station ON inspections(station_id);
CREATE INDEX idx_inspections_batch ON inspections(batch_number);

-- =====================================================
-- BẢNG: defect_summary (Thống kê lỗi theo ngày)
-- Mô tả: Tổng hợp tỷ lệ lỗi theo ngày/trạm
-- =====================================================
CREATE TABLE defect_summary (
    id SERIAL PRIMARY KEY,
    
    -- Thời gian
    summary_date DATE NOT NULL,
    station_id VARCHAR(50),
    
    -- Thống kê tổng quát
    total_inspected INT DEFAULT 0,                   -- Tổng sản phẩm kiểm tra
    total_passed INT DEFAULT 0,                      -- Số sản phẩm PASS
    total_failed INT DEFAULT 0,                      -- Số sản phẩm FAIL
    pass_rate FLOAT,                                 -- Tỷ lệ PASS (%)
    
    -- Thống kê theo loại lỗi
    missing_component_count INT DEFAULT 0,           -- Số lỗi thiếu linh kiện
    qr_error_count INT DEFAULT 0,                    -- Số lỗi QR
    sn_error_count INT DEFAULT 0,                    -- Số lỗi SN
    antenna_error_count INT DEFAULT 0,               -- Số lỗi anten
    
    -- Chi tiết lỗi phổ biến
    top_missing_components JSONB,                    -- Top linh kiện thiếu
    -- Ví dụ: [{"component": "C2", "count": 15}, {"component": "Anten1", "count": 8}]
    
    top_qr_errors JSONB,                             -- Top lỗi QR
    top_sn_errors JSONB,                             -- Top lỗi SN
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(summary_date, station_id)
);

-- =====================================================
-- BẢNG: alerts (Cảnh báo)
-- Mô tả: Lưu các cảnh báo khi tỷ lệ lỗi vượt ngưỡng
-- =====================================================
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    
    -- Thông tin cảnh báo
    alert_type VARCHAR(50) NOT NULL,                 -- HIGH_DEFECT_RATE / MISSING_COMPONENT / QR_ERROR / etc.
    severity VARCHAR(20) NOT NULL,                   -- INFO / WARNING / CRITICAL
    
    -- Nội dung
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    -- Liên kết
    station_id VARCHAR(50),
    product_type VARCHAR(100),
    batch_number VARCHAR(50),
    
    -- Trạng thái
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- BẢNG: users (Người dùng)
-- =====================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'operator',             -- admin / manager / operator
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Quan hệ bảng

```
product_templates (1) ──── (N) inspections
       │
       │ product_type
       │
       ▼
inspections (N) ──── (1) defect_summary
       │                    │
       │ station_id         │ station_id
       │                    │
       ▼                    ▼
    alerts              users
```

---

## 7. API & EXPORT

### 7.1 REST API Endpoints

#### Inspections

| Method | Endpoint | Mô tả | Tham số |
|--------|----------|-------|---------|
| GET | `/api/v1/inspections` | Danh sách kiểm tra | `page`, `limit`, `date_from`, `date_to`, `result`, `station` |
| GET | `/api/v1/inspections/{id}` | Chi tiết 1 lần kiểm tra | - |
| POST | `/api/v1/inspections` | Tạo kết quả kiểm tra mới | Body: inspection data |
| GET | `/api/v1/inspections/stats` | Thống kê tổng quan | `date_from`, `date_to` |

#### Export

| Method | Endpoint | Mô tả | Tham số |
|--------|----------|-------|---------|
| GET | `/api/v1/export/excel` | Export Excel | `date_from`, `date_to`, `station` |
| GET | `/api/v1/export/csv` | Export CSV | `date_from`, `date_to`, `station` |
| GET | `/api/v1/export/sql` | Export SQL dump | `date_from`, `date_to` |

#### Defects

| Method | Endpoint | Mô tả | Tham số |
|--------|----------|-------|---------|
| GET | `/api/v1/defects/summary` | Thống kê lỗi theo ngày | `date_from`, `date_to`, `station` |
| GET | `/api/v1/defects/trend` | Xu hướng lỗi | `days`, `station` |
| GET | `/api/v1/defects/top` | Top lỗi phổ biến | `date_from`, `date_to`, `limit` |

#### Templates

| Method | Endpoint | Mô tả | Tham số |
|--------|----------|-------|---------|
| GET | `/api/v1/templates` | Danh sách template | - |
| POST | `/api/v1/templates` | Tạo template mới | Body: template data |
| PUT | `/api/v1/templates/{id}` | Cập nhật template | Body: template data |
| DELETE | `/api/v1/templates/{id}` | Xóa template | - |

#### Alerts

| Method | Endpoint | Mô tả | Tham số |
|--------|----------|-------|---------|
| GET | `/api/v1/alerts` | Danh sách cảnh báo | `is_read`, `severity` |
| PUT | `/api/v1/alerts/{id}/read` | Đánh dấu đã đọc | - |
| PUT | `/api/v1/alerts/{id}/resolve` | Đánh dấu đã giải quyết | - |

#### Dashboard

| Method | Endpoint | Mô tả | Tham số |
|--------|----------|-------|---------|
| GET | `/api/v1/dashboard/stats` | Thống kê dashboard | - |
| GET | `/api/v1/dashboard/realtime` | Dữ liệu thời gian thực | - |

### 7.2 Export Excel chi tiết

```python
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

def export_inspection_report(date_from: str, date_to: str, station_id: str = None) -> str:
    """
    Xuất báo cáo kiểm tra chất lượng ra file Excel
    
    Args:
        date_from: Ngày bắt đầu (YYYY-MM-DD)
        date_to: Ngày kết thúc (YYYY-MM-DD)
        station_id: Mã trạm (None = tất cả)
    
    Returns:
        Đường dẫn file Excel
    """
    engine = create_engine(DATABASE_URL)
    
    # Query dữ liệu
    query = """
        SELECT 
            i.product_serial,
            i.product_type,
            i.batch_number,
            i.station_id,
            i.inspection_time,
            i.overall_result,
            i.missing_components,
            i.qr_result,
            i.qr_content,
            i.qr_error_detail,
            i.sn_result,
            i.sn_content,
            i.sn_error_detail,
            i.antenna_result,
            i.antenna_error_detail,
            i.inference_time_ms
        FROM inspections i
        WHERE i.inspection_time BETWEEN :date_from AND :date_to
    """
    
    params = {"date_from": date_from, "date_to": date_to}
    
    if station_id:
        query += " AND i.station_id = :station_id"
        params["station_id"] = station_id
    
    query += " ORDER BY i.inspection_time DESC"
    
    df = pd.read_sql(query, engine, params=params)
    
    # Tạo file Excel với nhiều sheet
    filename = f"inspection_report_{date_from}_{date_to}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        
        # Sheet 1: Chi tiết kiểm tra
        df.to_excel(writer, sheet_name='Chi tiết kiểm tra', index=False)
        
        # Sheet 2: Thống kê theo ngày
        df['date'] = pd.to_datetime(df['inspection_time']).dt.date
        daily_stats = df.groupby('date').agg(
            total=('overall_result', 'count'),
            passed=('overall_result', lambda x: (x == 'PASS').sum()),
            failed=('overall_result', lambda x: (x == 'FAIL').sum())
        ).reset_index()
        daily_stats['pass_rate'] = (daily_stats['passed'] / daily_stats['total'] * 100).round(2)
        daily_stats.to_excel(writer, sheet_name='Thống kê theo ngày', index=False)
        
        # Sheet 3: Thống kê theo trạm
        station_stats = df.groupby('station_id').agg(
            total=('overall_result', 'count'),
            passed=('overall_result', lambda x: (x == 'PASS').sum()),
            failed=('overall_result', lambda x: (x == 'FAIL').sum())
        ).reset_index()
        station_stats['pass_rate'] = (station_stats['passed'] / station_stats['total'] * 100).round(2)
        station_stats.to_excel(writer, sheet_name='Thống kê theo trạm', index=False)
        
        # Sheet 4: Top lỗi
        failed_df = df[df['overall_result'] == 'FAIL']
        
        # Top thiếu linh kiện
        missing_list = []
        for components in failed_df['missing_components'].dropna():
            if isinstance(components, list):
                missing_list.extend(components)
        missing_counts = pd.Series(missing_list).value_counts().reset_index()
        missing_counts.columns = ['Linh kiện', 'Số lần thiếu']
        
        # Top lỗi QR
        qr_errors = failed_df[failed_df['qr_result'] == 'FAIL']['qr_error_detail'].value_counts().reset_index()
        qr_errors.columns = ['Loại lỗi QR', 'Số lần']
        
        # Top lỗi SN
        sn_errors = failed_df[failed_df['sn_result'] == 'FAIL']['sn_error_detail'].value_counts().reset_index()
        sn_errors.columns = ['Loại lỗi SN', 'Số lần']
        
        # Top lỗi Anten
        antenna_errors = failed_df[failed_df['antenna_result'] == 'FAIL']['antenna_error_detail'].value_counts().reset_index()
        antenna_errors.columns = ['Loại lỗi Anten', 'Số lần']
        
        # Ghi vào sheet
        missing_counts.to_excel(writer, sheet_name='Top lỗi', index=False, startrow=0)
        qr_errors.to_excel(writer, sheet_name='Top lỗi', index=False, startrow=len(missing_counts) + 3)
        sn_errors.to_excel(writer, sheet_name='Top lỗi', index=False, startrow=len(missing_counts) + len(qr_errors) + 6)
        antenna_errors.to_excel(writer, sheet_name='Top lỗi', index=False, startrow=len(missing_counts) + len(qr_errors) + len(sn_errors) + 9)
        
        # Sheet 5: Thống kê theo batch
        batch_stats = df.groupby('batch_number').agg(
            total=('overall_result', 'count'),
            passed=('overall_result', lambda x: (x == 'PASS').sum()),
            failed=('overall_result', lambda x: (x == 'FAIL').sum())
        ).reset_index()
        batch_stats['pass_rate'] = (batch_stats['passed'] / batch_stats['total'] * 100).round(2)
        batch_stats.to_excel(writer, sheet_name='Thống kê theo batch', index=False)
    
    return filename
```

### 7.3 Export SQL

```python
def export_sql_dump(date_from: str, date_to: str) -> str:
    """
    Xuất dữ liệu kiểm tra ra file SQL
    """
    engine = create_engine(DATABASE_URL)
    
    query = """
        SELECT * FROM inspections
        WHERE inspection_time BETWEEN :date_from AND :date_to
        ORDER BY inspection_time DESC
    """
    
    df = pd.read_sql(query, engine, params={"date_from": date_from, "date_to": date_to})
    
    filename = f"inspection_dump_{date_from}_{date_to}.sql"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"-- AI Quality Control - Data Export\n")
        f.write(f"-- Date range: {date_from} to {date_to}\n")
        f.write(f"-- Total records: {len(df)}\n")
        f.write(f"-- Generated: {datetime.now()}\n\n")
        
        f.write("BEGIN;\n\n")
        
        for _, row in df.iterrows():
            columns = ', '.join(df.columns)
            values = ', '.join([f"'{str(v)}'" if v is not None else 'NULL' for v in row])
            f.write(f"INSERT INTO inspections ({columns}) VALUES ({values});\n")
        
        f.write("\nCOMMIT;\n")
    
    return filename
```

---

## 8. DASHBOARD & GIAO DIỆN

### 8.1 Layout tổng quan

```
┌─────────────────────────────────────────────────────────────────────┐
│  🏭 AI Quality Control                    [🔔 Alerts] [👤 User]    │
├──────────┬──────────────────────────────────────────────────────────┤
│          │                                                          │
│ Dashboard│  📊 Tổng quan hôm nay                                   │
│          │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ Inspect  │  │ Kiểm tra │ │   PASS   │ │   FAIL   │ │ Tỷ lệ   │   │
│          │  │  1,250   │ │  1,180   │ │    70    │ │  5.6%   │   │
│ Reports  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│          │                                                          │
│ Templates│  📈 Xu hướng tỷ lệ lỗi (30 ngày)                       │
│          │  ┌─────────────────────────────────────────────┐        │
│ Alerts   │  │     ╭─╮                                     │        │
│          │  │   ╭─╯ ╰─╮    ╭─╮                           │        │
│ Settings │  │ ╭─╯     ╰────╯ ╰─╮                         │        │
│          │  │─╯                 ╰───────────────────────  │        │
│          │  └─────────────────────────────────────────────┘        │
│          │                                                          │
│          │  🔴 Top lỗi hôm nay                                     │
│          │  ┌─────────────────────────────────────────────┐        │
│          │  │ Thiếu linh kiện    │ 35 │ ████████████ 50%  │        │
│          │  │ Sai QR             │ 18 │ ██████      26%   │        │
│          │  │ Lệch anten         │ 12 │ ████        17%   │        │
│          │  │ Sai SN             │  5 │ ██           7%   │        │
│          │  └─────────────────────────────────────────────┘        │
│          │                                                          │
│          │  📦 Chi tiết gần đây                                    │
│          │  ┌─────────────────────────────────────────────┐        │
│          │  │ SN-2026-A12345 │ PASS │ 22:10 │ OK          │        │
│          │  │ SN-2026-A12346 │ FAIL │ 22:09 │ QR sai      │        │
│          │  │ SN-2026-A12347 │ PASS │ 22:08 │ OK          │        │
│          │  └─────────────────────────────────────────────┘        │
│          │                                                          │
│          │  [📥 Export Excel] [📥 Export SQL] [🔄 Refresh]          │
└──────────┴──────────────────────────────────────────────────────────┘
```

### 8.2 Các trang chính

| Trang | Chức năng |
|-------|-----------|
| **Dashboard** | Tổng quan: tỷ lệ PASS/FAIL, xu hướng, top lỗi |
| **Inspections** | Danh sách chi tiết từng lần kiểm tra |
| **Reports** | Xem & xuất báo cáo (Excel, SQL, CSV) |
| **Templates** | Quản lý template sản phẩm |
| **Alerts** | Xem & quản lý cảnh báo |
| **Settings** | Cài đặt hệ thống |

---

## 9. PHÂN TÍCH CHI PHÍ & ROI

### 9.1 Chi phí triển khai

| Hạng mục | Chi phí (VNĐ) | Ghi chú |
|----------|---------------|---------|
| **Camera công nghiệp** (3 chiếc) | 6,000,000 - 15,000,000 | 2-5 triệu/chiếc |
| **Đèn LED chiếu sáng** (3 bộ) | 1,500,000 - 3,000,000 | 500k-1 triệu/bộ |
| **Giá đỡ camera** (3 chiếc) | 600,000 - 1,500,000 | 200k-500k/chiếc |
| **Edge computing** (Jetson/PC) | 2,000,000 - 20,000,000 | Tùy chọn |
| **Server** (nếu dùng cloud) | 500,000 - 2,000,000/tháng | Cloud hosting |
| **Phát triển phần mềm** | 50,000,000 - 100,000,000 | 2-3 tháng dev |
| **Training AI model** | 5,000,000 - 10,000,000 | GPU + data collection |
| **Tổng cộng** | **65,600,000 - 151,500,000** | |

### 9.2 Chi phí vận hành hàng tháng

| Hạng mục | Chi phí/tháng (VNĐ) |
|----------|---------------------|
| Cloud hosting | 500,000 - 2,000,000 |
| Bảo trì phần mềm | 2,000,000 - 5,000,000 |
| Điện năng | 200,000 - 500,000 |
| **Tổng/tháng** | **2,700,000 - 7,500,000** |

### 9.3 ROI (Return on Investment)

**Giả định:**
- Nhà máy sản xuất 1.000 sản phẩm/ngày
- Hiện tại: 5 công nhân QC, lương 8 triệu/tháng/người = 40 triệu/tháng
- Tỷ lệ lỗi sót hiện tại: 5% = 50 sản phẩm lỗi/ngày

**Sau khi dùng AI:**

| Chỉ số | Trước AI | Sau AI | Cải thiện |
|--------|----------|--------|------------|
| Nhân sự QC | 5 người | 1 người | Giảm 80% |
| Chi phí nhân sự | 40 triệu/tháng | 8 triệu/tháng | Tiết kiệm 32 triệu/tháng |
| Tốc độ kiểm tra | 100 SP/giờ | 1.000 SP/giờ | Tăng 10x |
| Tỷ lệ lỗi sót | 5% | <0.1% | Giảm 98% |
| Sản phẩm lỗi/ngày | 50 SP | <1 SP | Giảm 98% |

**ROI calculation:**
```
Chi phí đầu tư ban đầu: ~100 triệu (trung bình)
Tiết kiệm hàng tháng: 32 triệu (nhân sự) + 10 triệu (giảm phế phẩm)
= 42 triệu/tháng

Thời gian hoàn vốn: 100 triệu / 42 triệu = ~2.4 tháng
```

**→ Hoàn vốn trong 2-3 tháng!**

---

## 10. ROADMAP TRIỂN KHAI

### Phase 1: MVP (Tuần 1-4)

| Tuần | Task | Chi tiết |
|------|------|----------|
| 1 | Setup infrastructure | Docker, PostgreSQL, FastAPI skeleton |
| 1 | Camera setup | Kết nối camera, chụp ảnh test |
| 2 | AI model - Linh kiện | Train YOLOv8 detect linh kiện |
| 2 | AI model - QR/SN | Tích hợp OCR + QR decode |
| 3 | AI model - Anten | Train detect vị trí anten |
| 3 | Backend API | REST API endpoints |
| 4 | Basic dashboard | React frontend cơ bản |
| 4 | Export Excel/SQL | Pandas export |

**Deliverable:** MVP chạy được, kiểm tra 4 chức năng cơ bản

### Phase 2: Production Ready (Tuần 5-8)

| Tuần | Task | Chi tiết |
|------|------|----------|
| 5 | Template system | CRUD templates, multi-product support |
| 5 | Alert system | Telegram alerts, threshold config |
| 6 | Dashboard polish | Charts, real-time updates |
| 6 | Multi-station support | Hỗ trợ nhiều trạm kiểm tra |
| 7 | Reporting | Báo cáo chi tiết, scheduled reports |
| 7 | User management | Auth, roles, permissions |
| 8 | Testing & QA | Unit tests, integration tests |
| 8 | Documentation | User manual, API docs |

**Deliverable:** Production-ready, deploy được

### Phase 3: Scale & Optimize (Tuần 9-12)

| Tuần | Task | Chi tiết |
|------|------|----------|
| 9 | Performance optimization | GPU optimization, batch inference |
| 9 | Model improvement | Fine-tune với data thật |
| 10 | Advanced analytics | Predictive maintenance, trend analysis |
| 10 | Integration | Tích hợp MES/ERP systems |
| 11 | Mobile app | Dashboard mobile (React Native) |
| 11 | Multi-language | Hỗ trợ tiếng Việt, tiếng Anh |
| 12 | Training & handover | Đào tạo, chuyển giao |

**Deliverable:** Hệ thống hoàn chỉnh, scalable

---

## 11. RỦI RO & GIẢI PHÁP

### 11.1 Rủi ro kỹ thuật

| Rủi ro | Mức độ | Giải pháp |
|--------|--------|----------|
| **AI accuracy không đạt** | Cao | Thu thập nhiều data training, fine-tune model |
| **Ánh sáng không đều** | Trung bình | Đèn LED công nghiệp, normalize ảnh |
| **Camera chất lượng kém** | Thấp | Dùng camera công nghiệp chuyên dụng |
| **Tốc độ inference chậm** | Trung bình | Dùng GPU, optimize model, batch inference |
| **Sản phẩm đa dạng** | Cao | Template system, dễ thêm sản phẩm mới |

### 11.2 Rủi ro vận hành

| Rủi ro | Mức độ | Giải pháp |
|--------|--------|----------|
| **Camera bị bụi/mờ** | Trung bình | Vệ sinh định kỳ, alert khi ảnh mờ |
| **Công nhân không tin AI** | Cung bình | Chạy song song AI + human, so sánh kết quả |
| **Thay đổi sản phẩm** | Thấp | Template system, dễ cập nhật |
| **Mất kết nối camera** | Thấp | Alert tự động, fallback sang chế độ thủ công |

### 11.3 Rủi ro kinh doanh

| Rủi ro | Mức độ | Giải pháp |
|--------|--------|----------|
| **Chi phí cao** | Trung bình | ROI 2-3 tháng, chứng minh bằng pilot |
| **Khách hàng không mua** | Trung bình | Demo miễn phí 1 tháng |
| **Đối thủ cạnh tranh** | Thấp | Focus vào thị trường VN, support tốt |

---

## 12. KẾT LUẬN

### 12.1 Tóm tắt

Dự án **AI Quality Control** giải quyết bài toán kiểm tra chất lượng sản phẩm điện tử trong sản xuất, với các lợi ích:

- ✅ **Tăng tốc độ:** 10x (100 → 1.000+ sản phẩm/giờ)
- ✅ **Giảm lỗi sót:** 98% (5% → <0.1%)
- ✅ **Giảm nhân sự:** 80% (5 người → 1 người)
- ✅ **Hoàn vốn nhanh:** 2-3 tháng
- ✅ **Lưu trữ & Báo cáo:** SQL, Excel, Dashboard

### 12.2 Khuyến nghị

1. **Bắt đầu với Pilot:** Chạy thử 1 dây chuyền trong 1 tháng
2. **Thu thập data:** Chụp ảnh sản phẩm thật để train AI
3. **Tối ưu dần:** Fine-tune model dựa trên kết quả thực tế
4. **Mở rộng:** Sau khi pilot thành công, triển khai toàn bộ nhà máy

### 12.3 Bước tiếp theo

- [ ] Xác nhận loại sản phẩm cần kiểm tra
- [ ] Thu thập ảnh mẫu (100-500 ảnh/sản phẩm)
- [ ] Lựa chọn camera & edge computing hardware
- [ ] Bắt đầu phát triển MVP

---

**Báo cáo được lập bởi:** AI Assistant  
**Ngày:** 31/05/2026  
**Phiên bản:** 1.0  
**Trạng thái:** Sẵn sàng triển khai

---

*Lazadata AI Quality Control — Kiểm tra chất lượng thông minh, sản xuất hiệu quả.* 🏭
