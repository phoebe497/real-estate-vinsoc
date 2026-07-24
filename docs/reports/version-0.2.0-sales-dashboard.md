# Báo cáo phiên bản v0.2.0 — Authentication và Sales Dashboard

**Ngày hoàn thành:** 22/06/2026  
**Trạng thái:** Hoàn thành  
**Phụ thuộc:** `v0.1.0`

## 1. Mục tiêu phiên bản

Phiên bản `v0.2.0` bổ sung khu vực vận hành nội bộ cho Admin và Sale:

- Đăng nhập an toàn.
- Phân quyền Admin/Sale.
- Quản lý Lead và tiến trình chăm sóc.
- Phân công Lead cho Sale.
- Ghi chú lịch sử chăm sóc.
- Quản lý Fallback Rules.
- Quản lý tài khoản nhân sự.

## 2. Công việc đã thực hiện

### 2.1. Authentication và bảo mật

- Bổ sung bảng `users`.
- Mật khẩu được băm bằng Argon2 qua `pwdlib`.
- JWT access token ký bằng thuật toán HS256.
- Token chứa `sub`, `role`, `iat`, `exp`.
- FastAPI dependency xác thực token và kiểm tra user còn hoạt động.
- RBAC cho hai vai trò `admin` và `sale`.
- Seed tài khoản Admin lần đầu.

### 2.2. Lead workflow

- Thêm `assigned_to_id` vào bảng `leads`.
- Tạo bảng `lead_notes`.
- Hỗ trợ trạng thái:
  - `new`
  - `contacted`
  - `qualified`
  - `closed`
  - `lost`
- Tìm kiếm Lead theo tên, điện thoại hoặc email.
- Phân công nhân viên và ghi chú sau cuộc gọi.

Migration:

```text
migrations/versions/20260622_02_auth_and_lead_workflow.py
```

### 2.3. API mới

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

### 2.4. Sales Dashboard

Các route:

```text
/admin/login
/admin
/admin/leads
/admin/fallback-rules
/admin/users
```

Chức năng UI:

- Thống kê Lead theo trạng thái.
- Tìm kiếm và xem chi tiết Lead.
- Cập nhật trạng thái.
- Phân công Sale.
- Thêm ghi chú chăm sóc.
- Tạo/xóa Fallback Rule.
- Admin tạo tài khoản Sale/Admin.
- Đăng xuất và bảo vệ route bằng JWT.

### 2.5. Sửa Docker Backend

Dependency Python ban đầu được cài tại `/root/.local`, trong khi container chạy bằng `appuser`, dẫn tới:

```text
alembic: Permission denied
```

Phương án sửa:

- Tạo virtual environment tại `/opt/venv`.
- Copy `/opt/venv` sang production image.
- Đặt `/opt/venv/bin` vào `PATH`.
- Chạy `python -m alembic` và `python -m uvicorn`.

Cách này giữ container chạy non-root và phù hợp với CI/CD.

## 3. Phương án kỹ thuật

### 3.1. Argon2 thay vì lưu mật khẩu trực tiếp

Database chỉ lưu password hash. Mật khẩu gốc không thể đọc ngược từ Database.

### 3.2. Dependency-based RBAC

Quyền được kiểm tra ở Backend bằng FastAPI dependency, không chỉ ẩn nút trên Frontend. Vì vậy gọi API trực tiếp khi không có quyền vẫn nhận HTTP 401/403.

### 3.3. Lead notes tách khỏi summary

`summary` được dành cho phần tổng hợp nhu cầu, đặc biệt khi nối AI sau này. Ghi chú thủ công của Sale được lưu trong `lead_notes` để có tác giả và thời gian rõ ràng.

### 3.4. Migration chạy trước Backend

Trong Docker Compose:

```text
python -m alembic upgrade head
python -m uvicorn ...
```

Backend chỉ khởi động sau khi schema được nâng cấp thành công.

## 4. Hướng dẫn sử dụng

### 4.1. Khởi động

```powershell
docker compose up --build
```

Mở:

```text
https://vsocintern.online/admin/login
```

Tài khoản demo:

```text
Email: admin@gmail.com
Password: admin123456789Aa@
```

Phải đổi mật khẩu và `JWT_SECRET_KEY` trước khi deploy production.

### 4.2. Quản lý Lead

1. Mở menu **Khách hàng**.
2. Tìm khách theo tên, số điện thoại hoặc email.
3. Chọn một Lead.
4. Cập nhật trạng thái hoặc Sale phụ trách.
5. Thêm ghi chú sau cuộc gọi.

### 4.3. Quản lý Fallback Rules

1. Mở **Fallback Rules**.
2. Chọn **Thêm quy tắc**.
3. Nhập từ khóa, độ ưu tiên và câu trả lời.
4. Lưu hoặc xóa quy tắc không còn sử dụng.

### 4.4. Quản lý nhân sự

1. Đăng nhập bằng Admin.
2. Mở **Nhân sự**.
3. Chọn **Tạo tài khoản**.
4. Nhập tên, email, mật khẩu ban đầu và vai trò.

## 5. Hướng dẫn kiểm thử

### 5.1. Backend tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Kết quả nghiệm thu: **14 tests passed**.

Các test bao phủ:

- Từ chối API quản trị khi không có token.
- Login và `/auth/me`.
- Cập nhật trạng thái Lead.
- Thêm Lead note.
- CRUD Fallback Rules.
- Migration upgrade/downgrade.
- API Public của phiên bản trước.

### 5.2. Lint

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests migrations
```

Kết quả mong đợi:

```text
All checks passed!
```

### 5.3. Frontend build

```powershell
cd FE
npm run build
```

Kết quả phải có các route `/admin`, `/admin/login`, `/admin/leads`, `/admin/fallback-rules` và `/admin/users`.

### 5.4. Test Auth API thủ công

```powershell
$body = @{
    email = "admin@gmail.com"
    password = "admin123456789Aa@"
} | ConvertTo-Json

$login = Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/v1/auth/login" `
    -ContentType "application/json" `
    -Body $body

$headers = @{ Authorization = "Bearer $($login.access_token)" }

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/auth/me" `
    -Headers $headers

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/admin/dashboard" `
    -Headers $headers
```

### 5.5. Test Docker

```powershell
docker compose ps
docker compose logs --tail 100 backend frontend database
```

Ba service phải ở trạng thái running; Backend và Database phải healthy.

## 6. Kết quả nghiệm thu

- 14/14 tests passed.
- Ruff sạch.
- Next.js production build thành công với 10 route.
- PostgreSQL migration lên revision `20260622_02` thành công.
- Login Admin và Dashboard API hoạt động trên Docker.
- API Users trả về tài khoản Admin seed.
- Backend, Frontend và Database hoạt động ổn định.

## 7. Giới hạn và phiên bản tiếp theo

Chưa thực hiện:

- Refresh token, đổi/quên mật khẩu và thu hồi token.
- Dashboard lịch sử hội thoại.
- Audit log.
- Conversation/Message API cho Chat Widget.
- AI Agent, RAG và structured lead extraction.

Phiên bản tiếp theo dự kiến tập trung vào Conversation layer trước khi nối AI.

