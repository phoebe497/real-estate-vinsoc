# DevOps v0.3.1 — Security và Environment Baseline

Ngày thực hiện: 22/06/2026  
Trạng thái: Hoàn thành

## 1. Mục tiêu

Tạo nền cấu hình an toàn trước khi xây dựng CI/CD và deploy lên VPS. Phiên bản này ngăn staging/production vô tình chạy bằng cấu hình local, loại credential khỏi Docker Compose và cung cấp template riêng cho từng môi trường.

## 2. Công việc đã thực hiện

### 2.1. Loại thông tin nhạy cảm khỏi mã nguồn

- Thay giá trị `AI_LOG_API_KEY` có hình dạng khóa thật trong `.env.example` bằng placeholder.
- Xóa PostgreSQL password, JWT secret và admin password hard-code khỏi `docker-compose.yml`.
- Docker Compose lấy credential từ file môi trường.
- Mở rộng `.gitignore` để bỏ qua tất cả `.env.*`, nhưng vẫn cho phép commit các file `*.example`.

Lưu ý: thay placeholder trong Git không vô hiệu hóa khóa cũ. Nếu khóa AI log cũ từng hoạt động, chủ sở hữu phải thu hồi hoặc rotate khóa tại dịch vụ cấp khóa.

### 2.2. Tách template môi trường

Các template hiện có:

- `.env.example`: local development và Docker local.
- `.env.staging.example`: VPS staging.
- `.env.production.example`: production.

Staging và production có database name, database user, JWT secret, admin account, CORS origin và public API URL riêng.

### 2.3. Production fail-fast validation

`src/config.py` hỗ trợ bốn môi trường:

- `development`
- `test`
- `staging`
- `production`

Khi `APP_ENV=staging` hoặc `production`, backend từ chối khởi động nếu:

- JWT secret ngắn hơn 32 ký tự hoặc còn là placeholder/default.
- Admin password là giá trị mặc định, placeholder hoặc ngắn hơn 12 ký tự.
- Database không phải PostgreSQL.
- `AUTO_CREATE_TABLES=true`; staging/production phải dùng Alembic.
- Production CORS chứa wildcard, localhost hoặc `127.0.0.1`.

CORS origins cũng được trim khoảng trắng và bỏ phần tử rỗng trước khi truyền cho FastAPI middleware.

### 2.4. Version

Backend và frontend được nâng từ `0.3.0` lên `0.3.1`.

## 3. Phương án kỹ thuật

### Secret injection

Compose dùng `${VARIABLE:?message}` cho các giá trị PostgreSQL bắt buộc. Vì vậy cấu hình thiếu sẽ dừng ngay tại bước đọc Compose thay vì tạo container với mật khẩu mặc định.

Backend vẫn nhận secret qua environment variables theo Pydantic Settings. File có secret thật chỉ tồn tại trên máy local/VPS hoặc GitHub Environment; không commit vào repository.

### Configuration validation

Validation được đặt trong `Settings` bằng Pydantic `model_validator`. Cùng một quy tắc được áp dụng cho mọi cách chạy: Docker, Uvicorn, test hoặc script. Đây là lớp bảo vệ cuối nếu workflow deploy cấu hình sai.

### Schema management

`AUTO_CREATE_TABLES=false` là bắt buộc ở staging/production. Schema được quản lý bằng migration:

```bash
python -m alembic upgrade head
```

Điều này giúp version database có lịch sử, có thể kiểm tra và hỗ trợ rollback có kiểm soát.

## 4. Kết quả

| Kiểm tra | Kết quả |
| --- | --- |
| Backend test suite | 22 passed |
| Ruff | All checks passed |
| Next.js production build | Thành công, 11 routes |
| Docker Compose config | Hợp lệ |
| Production unsafe-config tests | Pass |

Các test cấu hình mới nằm tại `tests/test_config.py`.

## 5. Hướng dẫn sử dụng local

### Bước 1: Tạo file môi trường

PowerShell:

```powershell
Copy-Item .env.example .env
```

Thay tối thiểu các giá trị sau trong `.env`:

```dotenv
POSTGRES_PASSWORD=<local-password>
JWT_SECRET_KEY=<local-secret>
ADMIN_PASSWORD=<local-admin-password>
```

Không commit `.env`.

### Bước 2: Chạy bằng Docker

```powershell
docker compose config
docker compose up --build -d
docker compose ps
```

Kiểm tra:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### Bước 3: Dừng hệ thống

```powershell
docker compose down
```

Không thêm `-v` nếu muốn giữ dữ liệu PostgreSQL local.

## 6. Chuẩn bị staging/production

Trên VPS, tạo file thật từ template tương ứng:

```bash
cp .env.staging.example .env.staging
cp .env.production.example .env.production
chmod 600 .env.staging .env.production
```

Thay toàn bộ placeholder. Nếu password database chứa ký tự đặc biệt trong `DATABASE_URL`, password phải được URL-encode.

Sinh JWT secret an toàn:

```bash
openssl rand -hex 32
```

Các domain `example.com` trong template chỉ là ví dụ và phải được thay bằng domain thật.

## 7. Hướng dẫn test

### Chạy toàn bộ backend tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v --tb=short
```

### Chạy riêng security configuration tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_config.py -v
```

### Lint backend

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests
```

### Build frontend

```powershell
Set-Location FE
npm run build
```

### Validate Docker Compose mà không chạy container

```powershell
docker compose --env-file .env.example config --quiet
```

### Test cơ chế chặn production

Tạo cấu hình production với `JWT_SECRET_KEY=development-only-change-me`, sau đó chạy backend. Kết quả mong đợi: ứng dụng dừng với thông báo `Unsafe deployment configuration` và chỉ rõ `JWT_SECRET_KEY` không hợp lệ.

## 8. Việc chưa nằm trong phiên bản này

- Chưa tạo production-specific Compose.
- Chưa build/push image lên GHCR.
- Chưa deploy VPS.
- Chưa cấu hình Cloudflare hoặc HTTPS.
- Chưa tự động backup/rollback.

Các phần trên thuộc các phiên bản DevOps tiếp theo, bắt đầu bằng v0.4.0 Production Docker.
