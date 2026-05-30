# 🏭 Quality Control System
## Hệ Thống Kiểm Tra Chất Lượng Bằng Computer Vision

**Phiên bản:** 1.0.0  
**Trạng thái:** Đang phát triển  
**Ngày bắt đầu:** 31/05/2026

---

## 📖 Giới thiệu

Hệ thống kiểm tra chất lượng sản phẩm điện tử bằng Computer Vision (không dùng AI/ML), có khả năng:
- ✅ Phát hiện thiếu linh kiện
- ✅ Kiểm tra mã QR
- ✅ Kiểm tra tem Serial Number (SN)
- ✅ Kiểm tra vị trí anten
- ✅ Xuất báo cáo Excel/SQL
- ✅ Dashboard theo dõi thời gian thực

## 🛠️ Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| **Backend** | Python 3.12, FastAPI, Celery |
| **CV Engine** | OpenCV, pyzbar, EasyOCR |
| **Database** | PostgreSQL 15, Redis 7 |
| **Frontend** | React 18, Tailwind CSS, Recharts |
| **Infrastructure** | Docker, Docker Compose, Nginx |
| **Export** | Pandas, openpyxl |
| **Alerts** | Telegram Bot API |

## 🚀 Cài đặt

### Yêu cầu
- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+

### Docker (Khuyến nghị)
```bash
# Clone
git clone https://github.com/your-username/quality-control.git
cd quality-control

# Cấu hình
cp .env.example .env
# Chỉnh sửa .env

# Khởi động
docker compose up -d --build

# Chạy migrations
docker compose exec api alembic upgrade head
```

### Local
```bash
# Tạo venv
python3 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Cấu hình
cp .env.example .env

# Chạy migrations
alembic upgrade head

# Chạy API
uvicorn api.app:app --reload --port 8000

# Chạy Frontend (terminal riêng)
cd frontend && npm install && npm run dev
```

## 📚 Tài liệu

| Tài liệu | Mô tả |
|-----------|-------|
| [REPORT.md](docs/REPORT.md) | Báo cáo chi tiết dự án |
| [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Kế hoạch triển khai |

## 📁 Cấu trúc thư mục

```
quality-control/
├── api/                    # FastAPI backend
│   └── routers/            # API endpoints
├── core/                   # CV Engine
├── models/                 # SQLAlchemy models
├── services/               # Business logic
├── frontend/               # React frontend
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── migrations/             # Alembic
├── templates/              # Ảnh template mẫu
├── docs/                   # Tài liệu
├── captures/               # Ảnh chụp
├── nginx/                  # Nginx config
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 📄 License

Private project.

---

*Quality Control System — Kiểm tra chất lượng thông minh, sản xuất hiệu quả.* 🏭
