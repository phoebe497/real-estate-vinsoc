# Hotfix DevOps - Docker Compose backend startup

## Mục tiêu

Xử lý lỗi khi chạy:

```powershell
docker compose up --build -d
```

Compose báo:

```text
Container c2-app-005-backend-1 Error dependency backend failed to start
```

## Nguyên nhân

Lỗi nằm ở service `backend`, cụ thể là bước khởi động backend chạy migration:

```text
python -m alembic upgrade head
```

Có 2 nguyên nhân nối tiếp nhau:

1. `DATABASE_URL` trong `docker-compose.yml` được ghép theo dạng URL có chứa password.
   Nếu password PostgreSQL có ký tự đặc biệt như `@`, URL sẽ bị parse sai.
   Backend từng cố kết nối tới host sai dạng `@database`.

2. Volume PostgreSQL đã tồn tại từ lần chạy trước.
   PostgreSQL chỉ dùng `POSTGRES_USER` / `POSTGRES_PASSWORD` khi khởi tạo volume lần đầu.
   Nếu sau đó đổi password trong `.env`, database trong volume cũ không tự đổi password theo.
   Vì vậy backend tiếp tục gặp lỗi xác thực password.

## Phương án đã áp dụng

### 1. Không đặt password trực tiếp trong `DATABASE_URL`

Trong `docker-compose.yml`, backend được đổi từ URL có password:

```yaml
DATABASE_URL: postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
```

sang URL không chứa password:

```yaml
DATABASE_URL: postgresql+psycopg://${POSTGRES_USER}@database:5432/${POSTGRES_DB}
PGPASSWORD: ${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}
```

Lý do: `psycopg/libpq` có thể đọc password qua `PGPASSWORD`, tránh lỗi parse URL khi password có ký tự đặc biệt.

### 2. Đồng bộ password role PostgreSQL trong volume hiện tại

Thêm script:

```text
scripts/dev/sync_postgres_password.sql
```

Script này lấy `POSTGRES_USER` và `POSTGRES_PASSWORD` từ environment của container database, sau đó cập nhật password của role PostgreSQL hiện tại.

Đã chạy:

```powershell
docker compose cp scripts/dev/sync_postgres_password.sql database:/tmp/sync_postgres_password.sql
docker compose exec -T database sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -f /tmp/sync_postgres_password.sql'
```

Kết quả:

```text
ALTER ROLE
```

## Kết quả kiểm thử

Đã chạy lại:

```powershell
docker compose up -d --build
```

Kết quả:

```text
Container c2-app-005-backend-1 Healthy
Container c2-app-005-frontend-1 Started
```

Kiểm tra trạng thái:

```powershell
docker compose ps
```

Backend hiện tại:

```text
c2-app-005-backend-1 Up ... (healthy)
```

Kiểm tra health endpoint:

```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

Kết quả:

```json
{"status":"ok","env":"development"}
```

## Cách test lại khi gặp lỗi tương tự

1. Xem log backend:

```powershell
docker compose logs backend --tail 120
```

2. Nếu thấy lỗi host dạng `@database`, kiểm tra `DATABASE_URL` có nhét password trực tiếp vào URL không.

3. Nếu thấy:

```text
FATAL: password authentication failed for user
```

và bạn đang dùng volume PostgreSQL cũ, chạy đồng bộ password:

```powershell
docker compose cp scripts/dev/sync_postgres_password.sql database:/tmp/sync_postgres_password.sql
docker compose exec -T database sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -f /tmp/sync_postgres_password.sql'
docker compose up -d --build
```

4. Nếu không cần giữ dữ liệu local, có thể reset sạch database:

```powershell
docker compose down -v
docker compose up -d --build
```

Lưu ý: `down -v` sẽ xoá volume PostgreSQL local, đồng nghĩa mất dữ liệu local hiện tại.

