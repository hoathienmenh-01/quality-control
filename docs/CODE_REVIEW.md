# 🔍 Code Review — QC System
## Ngày: 2026-05-31

---

## 🔴 Critical Issues (PHẢI sửa)

### 1. Hardcoded SECRET_KEY — LỖ HỔNG BẢO MẬT NGHIÊM TRỌNG
**File:** `api/auth.py` dòng 13, `config.py` dòng 18
```python
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
```
**Vấn đề:** Nếu quên set env var, secret key mặc định sẽ được dùng → attacker có thể forge JWT token.
**Sửa:** Bắt buộc phải có SECRET_KEY, nếu không thì raise error khi khởi động.

### 2. CORS allow_origins=["*"] — LỖ HỔNG BẢO MẬT
**File:** `api/app.py` dòng 20
```python
allow_origins=["*"],
```
**Vấn đề:** Cho phép BẤT KỲ domain nào gọi API → CSRF, data theft.
**Sửa:** Chỉ cho phép domain frontend (VD: `http://localhost:3000`, domain production).

### 3. Component Detector — match_components quá yếu
**File:** `core/component_detector.py` dòng 163-196
```python
# Fallback: match by count
for i, comp in enumerate(detected):
    if i not in used_indices:
        best_match = comp
        best_idx = i
        break
```
**Vấn đề:** Khi không có position reference, nó match đại theo thứ tự → R1 có thể match nhầm vào C1. Đây là **logic sai nghiêm trọng** cho hệ thống QC thực tế.
**Sửa:** Bắt buộc phải có position reference cho mỗi component trong template. Không cho phép fallback theo count.

### 4. Inspection Pipeline — crop_roi gọi sai cách
**File:** `core/pipeline.py` dòng 51
```python
self.image_processor.crop_roi(processed, **qr_region)
```
**Vấn đề:** `qr_region` là dict `{x, y, w, h}` nhưng `crop_roi` nhận args `(image, x, y, w, h)`. Nếu `qr_region` có key khác (VD: `width` thay vì `w`), sẽ crash.
**Sửa:** Validate qr_region format trước khi gọi.

### 5. QR Checker — read_all_qrs không có error handling cho pyzbar
**File:** `core/qr_checker.py` dòng 84-94
```python
def read_all_qrs(self, image: np.ndarray) -> list:
    if not HAS_PYZBAR:
        raise ImportError("pyzbar not installed...")
    decoded = pyzbar_decode(image, symbols=[ZBarSymbol.QRCODE])
```
**Vấn đề:** `pyzbar_decode` có thể crash với ảnh corrupt, ảnh quá lớn, hoặc ảnh có format lạ. Không có try-except.
**Sửa:** Wrap pyzbar_decode trong try-except, return [] nếu lỗi.

### 6. SN Checker — clean_sn loại bỏ quá nhiều ký tự
**File:** `core/sn_checker.py` dòng 130
```python
cleaned = re.sub(r'[^A-Za-z0-9\-_]', '', text)
```
**Vấn đề:** Regex này loại bỏ khoảng trắng, nhưng SN có thể có format `SN 123 456` (có space). Nếu OCR đọc đúng nhưng có space, sẽ bị clean thành `SN123456` → mismatch với format gốc.
**Sửa:** Chỉ loại bỏ ký tự đặc biệt, giữ lại space nếu SN format cho phép.

---

## 🟡 Warnings (NÊN sửa)

### 7. Dùng config không nhất quán
**Vấn đề:** Có `config.py` (pydantic-settings) nhưng `api/auth.py` lại dùng `os.getenv()` trực tiếp. Hai nguồn config khác nhau → dễ gây confusion.
**Sửa:** Toàn bộ dùng `config.settings` từ `config.py`.

### 8. Database session không được inject đúng cách
**File:** `core/pipeline.py`, `core/qr_checker.py`, `core/sn_checker.py`
```python
def __init__(self, db_session=None):
    self.db = db_session
```
**Vấn đề:** `db_session` là optional nhưng các method như `check()` gọi `self.db.exists_qr()` mà không kiểm tra `self.db` có None không (chỉ check ở 1 số chỗ). Có thể crash nếu db=None.
**Sửa:** Thêm guard check `if self.db:` trước mọi lần gọi `self.db.xxx()`.

### 9. Annotator.save_annotated trả về path nhưng không đảm bảo thư mục tồn tại
**File:** `core/annotator.py` (chưa đọc nhưng được gọi trong pipeline)
**Vấn đề:** Nếu thư mục `captures/` chưa tồn tại, có thể crash.
**Sửa:** `os.makedirs(dir, exist_ok=True)` trước khi save.

### 10. Frontend dùng mock data thay vì gọi API
**File:** `frontend/src/stores/dashboardStore.js`
```javascript
stats: {
    total_inspected: 1250,  // ← hardcoded mock data
    total_passed: 1180,
}
```
**Vấn đề:** Stats luôn hiển thị mock data. `fetchStats()` chỉ được gọi nhưng nếu fail thì giữ mock data → user không biết data là giả.
**Sửa:** Thêm indicator "Dữ liệu mẫu" hoặc load từ API thực sự.

### 11. Frontend không có error boundary
**Vấn đề:** Nếu 1 component crash (VD: chart library lỗi), toàn bộ app sẽ trắng.
**Sửa:** Thêm React Error Boundary.

### 12. bcrypt warning trên Python 3.12
**Vấn đề:** `passlib` chưa tương thích hoàn toàn với bcrypt mới → warning mỗi lần hash.
**Sửa:** Dùng `bcrypt` trực tiếp thay vì qua `passlib`, hoặc pin version bcrypt.

### 13. requirements.txt thiếu version pin cho nhiều package
**File:** `requirements.txt`
```
opencv-python
pyzbar
easyocr
```
**Vấn đề:** Không pin version → có thể break khi cài trên máy khác.
**Sửa:** Pin version: `opencv-python==4.9.0.80`.

### 14. Dockerfile không có health check
**File:** `Dockerfile`
**Sửa:** Thêm `HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1`.

### 15. Inspection model thiếu created_at index
**File:** `models/inspection.py`
**Vấn đề:** Query theo thời gian (dashboard, reports) sẽ chậm trên hàng triệu bản ghi.
**Sửa:** Thêm index cho `created_at`.

### 16. Frontend — chart components dùng mock data
**File:** `frontend/src/components/charts/*.jsx`
**Vấn đề:** Tất cả chart đều dùng `MOCK_DATA` hardcoded, không fetch từ API.
**Sửa:** Fetch data từ API hoặc ít nhất có placeholder "Chưa có dữ liệu".

---

## 🟢 Good Practices (Làm tốt)

1. **CV Engine design:** Tách rời từng detector (Component, QR, SN, Anten) → dễ test, dễ maintain.
2. **Lazy loading OCR:** `SNChecker._get_reader()` chỉ load EasyOCR khi cần → tiết kiệm memory.
3. **Multi-try OCR:** `multi_try_ocr()` thử 6 strategies khác nhau → tăng accuracy.
4. **NMS algorithm:** `ComponentDetector._nms()` implement chuẩn → loại bỏ trùng lặp tốt.
5. **Annotated images:** Pipeline vẽ kết quả lên ảnh → trực quan cho operator.
6. **Retry logic:** `inspect_with_retry()` và `inspect_from_camera()` có retry → robust.
7. **Template matching đa tỷ lệ:** `multi_scale_template_match()` với 5 scales → phát hiện linh kiện ở nhiều kích thước.
8. **Shape classification:** `classify_shape()` phân loại hình dạng → useful cho debugging.
9. **Frontend component structure:** Tách charts, shared components, stores → clean architecture.
10. **Zustand stores:** Dùng Zustand thay vì Redux → đơn giản, ít boilerplate.
11. **Sub-pixel accuracy:** AntenChecker dùng moments để tính center → chính xác hơn boundingRect.
12. **Config centralized:** `config.py` dùng pydantic-settings → type-safe config.

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total files reviewed | 25 |
| Total lines (Python) | ~2,800 |
| Total lines (JS/JSX) | ~6,500 |
| Critical issues | 6 |
| Warnings | 10 |
| Good practices | 12 |

---

## 📝 Ưu tiên sửa

| Ưu tiên | Issue | Impact |
|---------|-------|--------|
| P0 | #1 Hardcoded SECRET_KEY | Security |
| P0 | #2 CORS * | Security |
| P0 | #3 match_components logic | Business logic |
| P1 | #4 crop_roi validation | Stability |
| P1 | #5 pyzbar error handling | Stability |
| P1 | #8 db_session guard | Stability |
| P2 | #6 SN clean logic | Accuracy |
| P2 | #7 Config inconsistency | Code quality |
| P2 | #10 Mock data indicator | UX |
| P3 | #11-16 Các warnings còn lại | Best practice |

---

## 🎯 Kết luận

**Code skeleton tốt** — kiến trúc sạch, tách module rõ ràng, CV engine có nhiều strategy hay.

**Tuy nhiên chưa sẵn sàng production** vì:
1. Lỗ hổng bảo mật (SECRET_KEY, CORS)
2. Logic matching components quá yếu (fallback theo count = random)
3. Error handling chưa đầy đủ (pyzbar, db_session)
4. Frontend toàn mock data

**Ước tính sửa:** ~2-3 ngày cho P0 + P1 issues.
