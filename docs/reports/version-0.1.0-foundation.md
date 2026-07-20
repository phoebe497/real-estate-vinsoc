# Báo cáo phiên bản v0.1.0 — Nền tảng FE, BE và Database

**Ngày hoàn thành:** 21/06/2026  
**Trạng thái:** Hoàn thành  
**Phạm vi:** Xây nền tảng ứng dụng trước khi tích hợp AI Agent.

## 1. Mục tiêu phiên bản

Phiên bản `v0.1.0` xây dựng một ứng dụng web bất động sản có thể hoạt động độc lập với AI:

- Đọc và hiển thị dữ liệu 12 phân khu căn hộ.
- Cung cấp trang danh sách và chi tiết phân khu.
- Thu thập nhu cầu khách hàng dưới dạng Lead.
- Chuẩn bị cấu trúc Database cho hội thoại và Fallback Rules.
- Đóng gói FE, BE và PostgreSQL bằng Docker Compose.

AI Agent và RAG chưa được nối vào luồng sản phẩm trong phiên bản này.

## 2. Công việc đã thực hiện

### 2.1. Database

Đã tạo các SQLAlchemy entities:

| Bảng | Chức năng |
|---|---|
| `subdivisions` | Thông tin 12 phân khu |
| `apartment_specs` | Loại căn, diện tích và giá |
| `amenities` | Tiện ích nội khu/ngoại khu |
| `sales_policies` | Chính sách bán hàng |
| `leads` | Khách hàng để lại nhu cầu |
| `conversations` | Phiên trò chuyện độc lập với Lead |
| `messages` | Tin nhắn thuộc phiên trò chuyện |
| `fallback_rules` | Câu trả lời khi thiếu dữ liệu |

Đã cấu hình Alembic và migration đầu tiên:

```text
migrations/versions/20260620_01_initial_schema.py
```

### 2.2. Chuẩn hóa dữ liệu

Đã tạo bộ seed đọc từ:

```text
cleaned_data/cleaned_apartment_zones.json
```

Seed nạp 12 phân khu, apartment specs, tiện ích và chính sách bán hàng. Seed chỉ chạy khi bảng phân khu chưa có dữ liệu nên không tạo bản ghi trùng khi container restart.

### 2.3. Backend API

Các endpoint được triển khai:

| Method | Endpoint | Chức năng |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/subdivisions` | Danh sách phân khu |
| `GET` | `/api/v1/subdivisions/{slug}` | Chi tiết phân khu |
| `POST` | `/api/v1/contact` | Validate và tạo Lead |

API danh sách hỗ trợ lọc theo trạng thái bàn giao, loại căn và giá tối đa.

### 2.4. Public Frontend

Đã xây dựng các route Next.js:

```text
/
/phan-khu
/phan-khu/[slug]
/lien-he
/_not-found
```

Chat Widget ở phiên bản này là UI placeholder, chưa gửi request tới AI.

### 2.5. Docker

Đã cấu hình ba service:

- PostgreSQL 16.
- FastAPI Backend.
- Next.js Frontend.

## 3. Phương án kỹ thuật

### 3.1. Tách AI khỏi nghiệp vụ nền

Website, Lead và Database được xây trước AI để:

- Có thể kiểm thử dữ liệu và nghiệp vụ bằng cách xác định.
- Không làm toàn hệ thống phụ thuộc LLM.
- Cho phép thay đổi Agent/RAG mà không sửa Public Website.

### 3.2. Chuẩn hóa giá và diện tích

Ngoài chuỗi gốc để hiển thị, hệ thống lưu thêm giá trị số:

- `area_min`, `area_max`.
- `price_min`, `price_max`.
- `area_note`, `price_note`.

Cách này vừa giữ đúng nội dung nguồn vừa hỗ trợ lọc/sắp xếp bằng Database.

### 3.3. Tách Conversation khỏi Lead

Khách có thể bắt đầu chat khi chưa cung cấp số điện thoại. Vì vậy `conversations.lead_id` được phép rỗng và chỉ liên kết Lead sau khi có thông tin liên hệ.

### 3.4. API URL trong Docker

Frontend sử dụng hai URL:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
API_URL_INTERNAL=http://backend:8000/api/v1
```

URL đầu dành cho trình duyệt; URL thứ hai dành cho Server Component chạy trong Frontend container. Điều này tránh lỗi 404 do `localhost` trong container trỏ về chính container Frontend.

## 4. Hướng dẫn sử dụng

### 4.1. Chạy bằng Docker

```powershell
docker compose up --build
```

Truy cập:

- Website: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 4.2. Chạy Backend local bằng SQLite

Tạo `.env.local`:

```dotenv
DATABASE_URL=sqlite:///./app.db
AUTO_CREATE_TABLES=true
AUTO_SEED_CATALOG=true
```

Chạy:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload --port 8000
```

### 4.3. Chạy Frontend local

```powershell
cd FE
npm install
npm run dev
```

## 5. Hướng dẫn kiểm thử

### 5.1. Automated tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tại thời điểm nghiệm thu phiên bản: **10 tests passed**.

### 5.2. Migration test

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_db\test_migrations.py -vv
```

Test thực hiện upgrade lên `head`, kiểm tra các bảng rồi downgrade về `base` trên Database tạm.

### 5.3. Frontend build

```powershell
cd FE
npm run build
```

### 5.4. Kiểm thử thủ công

1. Mở `/phan-khu` và xác nhận có 12 phân khu.
2. Chọn The Zenpark và xác nhận trang chi tiết không trả 404.
3. Kiểm tra bảng loại căn, tiện ích và chính sách.
4. Gửi form với số điện thoại hợp lệ.
5. Gửi lại với số điện thoại sai và xác nhận nhận lỗi validation.

Kiểm tra API trực tiếp:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/subdivisions
Invoke-RestMethod http://localhost:8000/api/v1/subdivisions/the-zenpark
```

## 6. Kết quả nghiệm thu

- Seed trả đúng 12 phân khu.
- Trang chi tiết The Zenpark trả HTTP 200.
- Backend tests đạt 10/10.
- Next.js production build thành công.
- Docker Compose configuration hợp lệ.

## 7. Giới hạn phiên bản

- Chưa có đăng nhập và phân quyền.
- Chưa có Sales Dashboard.
- Chưa có Conversation API thực tế.
- Chưa tích hợp AI Agent/RAG.

