# Báo cáo triển khai Giai đoạn 1 — FE, BE và Database trước AI Agent

> **Lưu ý:** Đây là báo cáo tổng hợp cũ. Báo cáo chính thức đã được tách theo phiên bản tại [`docs/reports/README.md`](reports/README.md). Từ các phiên bản tiếp theo, mỗi phiên bản sẽ có một report độc lập.

**Ngày cập nhật:** 21/06/2026  
**Phạm vi:** Nền tảng website công khai, Backend API và Database trước khi tích hợp AI Agent/RAG.

## 1. Mục tiêu giai đoạn

Giai đoạn này xây dựng phần ứng dụng web thông thường để AI Agent có thể được tích hợp sau dưới dạng một mô-đun độc lập. Hệ thống hiện tập trung vào các luồng:

- Hiển thị danh sách 12 phân khu căn hộ Vinhomes Ocean Park 1.
- Hiển thị thông tin chi tiết của từng phân khu.
- Tiếp nhận nhu cầu tư vấn và lưu Lead.
- Chuẩn bị cấu trúc lưu phiên hội thoại, tin nhắn và Fallback Rules.
- Cung cấp giao diện Chat Widget ở trạng thái chờ, chưa gọi LLM hoặc Agent.
- Chạy toàn bộ FE, BE và PostgreSQL bằng Docker Compose.

## 2. Những phần đã thực hiện

### 2.1. Database và Data Layer

Đã bổ sung SQLAlchemy 2 và các entity sau:

| Bảng | Mục đích |
|---|---|
| `subdivisions` | Thông tin 12 phân khu căn hộ |
| `apartment_specs` | Loại căn, diện tích và khoảng giá |
| `amenities` | Tiện ích nội khu và ngoại khu |
| `sales_policies` | Chính sách bán hàng theo phân khu |
| `leads` | Thông tin khách hàng cần tư vấn |
| `conversations` | Phiên trò chuyện của khách, kể cả khách vãng lai |
| `messages` | Nội dung tin nhắn thuộc từng phiên chat |
| `fallback_rules` | Câu trả lời do Sale cấu hình khi thiếu dữ liệu |

Các thay đổi quan trọng so với thiết kế ban đầu:

- Diện tích được tách thành `area_min` và `area_max` dạng số.
- Giá được tách thành `price_min` và `price_max` dạng số, đơn vị VND.
- Vẫn giữ `area_note` và `price_note` để hiển thị đúng nội dung nguồn.
- Tách `conversations` và `messages` thay cho một bảng `chat_history` phẳng.
- `conversation.lead_id` có thể rỗng để hỗ trợ khách chưa cung cấp số điện thoại.
- Bổ sung trạng thái xuất bản, thứ tự hiển thị và timestamps.

Mã nguồn chính:

- `src/db/base.py`: Declarative Base của SQLAlchemy.
- `src/db/session.py`: Engine, Session Factory và FastAPI dependency.
- `src/db/seed.py`: Nạp dữ liệu sạch cho 12 phân khu.
- `src/models/entities.py`: Toàn bộ ORM entities.

### 2.2. Migration

Đã cấu hình Alembic và tạo migration đầu tiên:

- `alembic.ini`
- `migrations/env.py`
- `migrations/versions/20260620_01_initial_schema.py`

Migration hỗ trợ tạo và rollback toàn bộ tám bảng của giai đoạn này.

### 2.3. Seed dữ liệu

Khi database chưa có phân khu, hệ thống đọc file:

```text
cleaned_data/cleaned_apartment_zones.json
```

Sau đó nạp:

- 12 phân khu.
- Các loại căn và khoảng giá/diện tích.
- Tiện ích nội khu, ngoại khu.
- Chính sách bán hàng.

Seed có tính idempotent: nếu bảng `subdivisions` đã có dữ liệu thì không nạp lại.

### 2.4. Backend API

Đã bổ sung các API public:

| Method | Endpoint | Chức năng |
|---|---|---|
| `GET` | `/health` | Kiểm tra Backend |
| `GET` | `/api/v1/subdivisions` | Danh sách phân khu đã xuất bản |
| `GET` | `/api/v1/subdivisions/{slug}` | Chi tiết một phân khu |
| `POST` | `/api/v1/contact` | Validate thông tin và tạo Lead |

API danh sách hỗ trợ các query parameters:

- `handover_status`
- `unit_type`
- `max_price`

Form Lead kiểm tra số điện thoại Việt Nam gồm 10 chữ số và bắt đầu bằng `0`. Email được kiểm tra đúng định dạng nếu người dùng cung cấp.

Mã nguồn chính:

- `src/api/catalog.py`
- `src/api/leads.py`
- `src/models/schemas.py`

### 2.5. Frontend Next.js

Đã dựng lại source Next.js với các route:

| Route | Nội dung |
|---|---|
| `/` | Hero, phân khu nổi bật và giá trị sản phẩm |
| `/phan-khu` | Danh sách 12 phân khu |
| `/phan-khu/[slug]` | Chi tiết, bảng giá, tiện ích, chính sách và form tư vấn |
| `/lien-he` | Form đăng ký tư vấn |
| `/_not-found` | Trạng thái không tìm thấy dữ liệu |

Các đặc điểm UI/UX:

- Dark mode, glass effect nhẹ và màu xanh mint.
- Responsive cho desktop, tablet và mobile.
- Có loading/fallback dữ liệu cơ bản khi Backend chưa hoạt động.
- Form liên hệ gọi API thật.
- Chat Widget hiện chỉ hiển thị thông báo và CTA liên hệ; chưa gọi AI.

Mã nguồn chính:

- `FE/src/app/`
- `FE/src/components/`
- `FE/src/lib/api.ts`
- `FE/src/app/globals.css`

### 2.6. Docker

`docker-compose.yml` hiện gồm ba service:

- `database`: PostgreSQL 16.
- `backend`: FastAPI, chạy Alembic trước khi khởi động.
- `frontend`: Next.js production server.

Frontend chạy tại cổng `3000`, Backend tại `8000`.

Frontend sử dụng hai địa chỉ API trong Docker:

- `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` cho request chạy trên trình duyệt.
- `API_URL_INTERNAL=http://backend:8000/api/v1` cho Server Component chạy bên trong container Frontend.

Không dùng `localhost` cho giao tiếp server-to-server giữa các container vì `localhost` bên trong Frontend container trỏ về chính container Frontend.

Backend image cài dependency vào virtual environment `/opt/venv`. Cách này cho phép user không đặc quyền `appuser` chạy Alembic và Uvicorn mà không cần truy cập thư mục `/root`.

## 3. Kết quả kiểm thử đã thực hiện

Tại thời điểm lập báo cáo:

- Backend: **10 tests passed**.
- Test API, validation, seed và migration đều đạt.
- Next.js production build thành công.
- Docker Compose configuration validation thành công.

Các test mới nằm tại:

- `tests/test_api/test_catalog.py`
- `tests/test_db/test_migrations.py`

## 4. Hướng dẫn chạy và kiểm thử

Tất cả câu lệnh dưới đây được chạy từ thư mục gốc dự án:

```powershell
cd "D:\Python\AI Real Estate Advisor\C2-App-005"
```

### 4.1. Cài dependency Backend

Nếu chưa có virtual environment:

```powershell
py -3.11 -m venv .venv
```

Kích hoạt môi trường và cài package:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Sao chép `.env.example` thành `.env` và điều chỉnh cấu hình nếu cần.

### 4.2. Chạy toàn bộ Backend tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Kết quả mong đợi:

```text
..........                                                               [100%]
10 passed
```

### 4.3. Chạy riêng test API

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_api -q
```

Nhóm test này xác minh:

- Health endpoint.
- Validation request chat hiện có.
- Seed đủ 12 phân khu.
- Lấy chi tiết The Zenpark.
- Tiện ích có cả `internal` và `external`.
- Tạo Lead thành công.
- Từ chối số điện thoại sai.

### 4.4. Chạy riêng test migration

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_db\test_migrations.py -vv
```

Test tạo một SQLite database tạm, chạy:

1. Alembic upgrade lên `head`.
2. Kiểm tra đủ tám bảng.
3. Alembic downgrade về `base`.

Database tạm được pytest tự quản lý và không ảnh hưởng database thật.

### 4.5. Kiểm tra code Backend

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests migrations
```

Kết quả mong đợi:

```text
All checks passed!
```

### 4.6. Chạy Backend với SQLite để phát triển nhanh

Để tránh ghi đè API key và các cấu hình dùng chung trong `.env`, tạo `.env.local` với nội dung:

```dotenv
DATABASE_URL=sqlite:///./app.db
AUTO_CREATE_TABLES=true
AUTO_SEED_CATALOG=true
```

Ứng dụng đọc `.env` trước và `.env.local` sau, vì vậy cấu hình local sẽ được ưu tiên. Docker Compose vẫn tự truyền URL PostgreSQL riêng cho container Backend.

Khởi động Backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload --port 8000
```

Kiểm tra:

- Health: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`
- Danh sách phân khu: `http://localhost:8000/api/v1/subdivisions`
- Chi tiết Zenpark: `http://localhost:8000/api/v1/subdivisions/the-zenpark`

### 4.7. Test API thủ công bằng PowerShell

Lấy danh sách phân khu:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/subdivisions"
```

Lọc phân khu có căn `2PN`:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/subdivisions?unit_type=2PN"
```

Tạo Lead:

```powershell
$body = @{
    name = "Nguyễn Văn An"
    phone = "0912345678"
    email = "an@example.com"
    preferred_bedrooms = "2PN"
    subdivision_slug = "the-zenpark"
    message = "Muốn nhận bảng giá mới"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/v1/contact" `
    -ContentType "application/json" `
    -Body $body
```

Kết quả mong đợi là HTTP `201` với `id`, trạng thái `new` và thời gian tạo.

### 4.8. Chạy và build Frontend

```powershell
cd FE
npm install
npm run dev
```

Mở `http://localhost:3000`.

Kiểm tra production build:

```powershell
npm run build
```

Các route mong đợi trong kết quả build:

```text
/
/_not-found
/lien-he
/phan-khu
/phan-khu/[slug]
```

### 4.9. Chạy toàn bộ hệ thống bằng Docker

Từ thư mục gốc:

```powershell
docker compose config --quiet
docker compose up --build
```

Sau khi các health check hoàn tất:

- Website: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

Kiểm tra container:

```powershell
docker compose ps
```

Dừng hệ thống nhưng giữ dữ liệu PostgreSQL:

```powershell
docker compose down
```

## 5. Checklist nghiệm thu thủ công

### Public Website

- [ ] Trang chủ hiển thị đúng trên desktop và mobile.
- [ ] Trang `/phan-khu` có 12 phân khu khi Backend hoạt động.
- [ ] Click một card mở đúng trang chi tiết.
- [ ] Trang chi tiết có vị trí, loại căn, giá, tiện ích và chính sách.
- [ ] Chat Widget mở/đóng được và chưa gửi request tới AI.

### Form Lead

- [ ] Số điện thoại hợp lệ tạo Lead thành công.
- [ ] Số điện thoại sai nhận lỗi validation.
- [ ] Slug phân khu không tồn tại bị từ chối.
- [ ] Form hiển thị trạng thái đang gửi, thành công và thất bại.

### Database

- [ ] Migration chạy lên `head` thành công.
- [ ] Database có đủ tám bảng.
- [ ] Seed tạo đúng 12 phân khu và không tạo trùng khi restart.
- [ ] Giá và diện tích có cả dữ liệu số và nội dung hiển thị gốc.

## 6. Cập nhật Giai đoạn 2 — Authentication và Sales Dashboard

Ngày 22/06/2026, hệ thống đã được bổ sung:

- Bảng `users` với vai trò `admin` và `sale`.
- Bảng `lead_notes` và trường phân công `assigned_to_id` trên Lead.
- Mật khẩu băm bằng Argon2, không lưu mật khẩu thô.
- JWT access token có thời hạn cấu hình được.
- Seed tài khoản Admin lần đầu, không tạo trùng khi restart.
- API đăng nhập, xem người dùng hiện tại và tạo tài khoản Sale/Admin.
- API thống kê Dashboard.
- API tìm kiếm, xem chi tiết và cập nhật trạng thái Lead.
- API ghi chú Lead.
- CRUD Fallback Rules có bảo vệ bằng RBAC.
- Giao diện `/admin/login`, `/admin`, `/admin/leads`, `/admin/fallback-rules` và `/admin/users`.
- UI phân công Lead cho Sale và ghi chú lịch sử chăm sóc.
- UI Admin tạo tài khoản Sale/Admin mới.

Migration mới:

```text
migrations/versions/20260622_02_auth_and_lead_workflow.py
```

Các API mới:

| Method | Endpoint | Quyền |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Public |
| `GET` | `/api/v1/auth/me` | Admin/Sale |
| `GET/POST` | `/api/v1/auth/users` | Admin |
| `GET` | `/api/v1/admin/dashboard` | Admin/Sale |
| `GET` | `/api/v1/admin/leads` | Admin/Sale |
| `GET/PATCH` | `/api/v1/admin/leads/{id}` | Admin/Sale |
| `POST` | `/api/v1/admin/leads/{id}/notes` | Admin/Sale |
| CRUD | `/api/v1/admin/fallback-rules` | Admin/Sale |

Tài khoản demo local/Docker:

```text
URL: https://vsocintern.online/admin/login
Email: admin@gmail.com
Password: admin123456789Aa@
```

Phải thay `JWT_SECRET_KEY` và mật khẩu Admin trước khi deploy production.

Kết quả xác minh Giai đoạn 2:

- **14 tests passed**.
- Ruff: `All checks passed!`.
- Next.js production build thành công với chín route.
- Alembic nâng PostgreSQL lên revision `20260622_02` thành công.
- Đăng nhập Admin, `/auth/me` và `/admin/dashboard` hoạt động trên Docker.
- Backend, Frontend và PostgreSQL đều healthy.

## 7. Phần chưa thực hiện

- Refresh token, thu hồi token và đổi/quên mật khẩu.
- Dashboard lịch sử Conversations.
- Quản trị nội dung phân khu.
- Audit log cho thay đổi dữ liệu quản trị.
- API tạo conversation/message cho Chat Widget.
- AI Agent, RAG, Vector Store và lead extraction tự động.

## 8. Hướng triển khai tiếp theo

1. Hoàn thiện UI người dùng Sale, phân công Lead và lịch sử hội thoại.
2. Xây API Conversation/Message độc lập với AI.
3. Bổ sung audit log và cấu hình production secrets.
4. Chạy kiểm thử bảo mật và phân quyền đầy đủ.
5. Sau đó mới nối LangGraph Agent, RAG và structured lead extraction.
