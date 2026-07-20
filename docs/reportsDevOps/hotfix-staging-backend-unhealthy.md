# Hotfix: staging backend unhealthy

## Bối cảnh

Khi chạy trên VPS:

```bash
bash scripts/deploy/staging_deploy.sh
```

Docker Compose báo lỗi:

```text
dependency failed to start: container ocean-park-staging-backend-1 is unhealthy
```

Lỗi này nghĩa là service `frontend` đang chờ `backend` healthy, nhưng backend không vượt qua healthcheck:

```text
http://localhost:8000/ready
```

Thông thường nguyên nhân nằm ở một trong các nhóm sau:

- Backend không start được.
- Alembic migration fail.
- Backend không kết nối được PostgreSQL.
- `.env` staging thiếu hoặc sai secret/config.
- Image cũ chưa chứa code/config mới.

## Nguyên nhân kỹ thuật cần ưu tiên kiểm tra

Trong `docker-compose.registry.yml`, backend trước đó tạo `DATABASE_URL` nội bộ không có password:

```yaml
DATABASE_URL: postgresql+psycopg://${POSTGRES_USER}@database:5432/${POSTGRES_DB}
```

Trong môi trường deploy thật, Alembic/SQLAlchemy nên nhận connection string đầy đủ, bao gồm password. Nếu không, backend có thể fail khi chạy:

```bash
python -m alembic upgrade head
```

hoặc fail khi endpoint `/ready` kiểm tra database.

## Phương án đã áp dụng

Cập nhật `docker-compose.registry.yml` để backend dùng `DATABASE_URL` có password:

```yaml
DATABASE_URL: postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
```

Cập nhật `.env.staging.example` để template cũng thể hiện đúng cấu trúc connection string:

```env
DATABASE_URL=postgresql+psycopg://ocean_staging:replace-with-a-unique-staging-database-password@database:5432/ocean_park_staging
```

## Việc user cần làm trên VPS

Vào project folder:

```bash
cd /opt/ocean-park-advisor
```

Pull code mới:

```bash
git checkout dev
git pull origin dev
```

Mở file `.env`:

```bash
nano .env
```

Kiểm tra các biến tối thiểu:

```env
POSTGRES_DB=ocean_park_staging
POSTGRES_USER=ocean_staging
POSTGRES_PASSWORD=<strong-db-password>
DATABASE_URL=postgresql+psycopg://ocean_staging:<strong-db-password>@database:5432/ocean_park_staging
AUTO_CREATE_TABLES=false
AUTO_SEED_CATALOG=true
JWT_SECRET_KEY=<random-secret-at-least-32-characters>
ADMIN_EMAIL=<your-admin-email>
ADMIN_PASSWORD=<strong-admin-password>
CORS_ORIGINS=http://<vps-ip>:3000
NEXT_PUBLIC_API_URL=http://<vps-ip>:8000/api/v1
BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
```

Lưu ý: nếu password có ký tự đặc biệt như `@`, `:`, `/`, `#`, `%`, nên đổi sang password chỉ gồm chữ/số/ký tự an toàn, hoặc URL encode password trong `DATABASE_URL`.

## Cách test và debug

Chạy lại deploy:

```bash
bash scripts/deploy/staging_deploy.sh
```

Script staging đã được cập nhật để nếu `docker compose up -d` fail, nó tự in:

- trạng thái container
- log database
- log backend

Nếu vẫn lỗi, xem log backend:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs backend --tail 200
```

Kiểm tra trạng thái container:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml ps
```

Kiểm tra database healthy:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs database --tail 100
```

Test readiness từ VPS:

```bash
curl http://localhost:8000/ready
```

Kết quả mong đợi:

```json
{"status":"ready","database":"ok"}
```

## Khi nào cần reset database volume?

Chỉ reset volume nếu log database/backend cho thấy database cũ đang dùng user/password cũ, ví dụ:

```text
password authentication failed
role does not exist
database does not exist
```

Khi đó cần cân nhắc vì thao tác này xóa dữ liệu staging hiện có:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml down
docker volume ls | grep ocean-park-staging
docker volume rm <postgres-volume-name>
bash scripts/deploy/staging_deploy.sh
```

Không dùng lệnh xóa volume nếu database staging đã có dữ liệu quan trọng.

## Nếu đã sửa DATABASE_URL nhưng backend vẫn unhealthy

Ưu tiên kiểm tra log backend:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs backend --tail 200
```

Các lỗi thường gặp và hướng xử lý:

### 1. Password authentication failed

Ví dụ:

```text
password authentication failed for user "ocean_staging"
```

Nguyên nhân thường là PostgreSQL volume đã được tạo từ lần chạy trước với password khác. Biến `POSTGRES_PASSWORD` mới trong `.env` không tự đổi password của database đã tồn tại.

Cách xử lý an toàn:

- Nếu chưa có dữ liệu staging quan trọng: xóa volume database rồi deploy lại.
- Nếu đã có dữ liệu: dùng lại password cũ hoặc đổi password trong PostgreSQL bằng SQL.

### 2. Role/database does not exist

Ví dụ:

```text
role "ocean_staging" does not exist
database "ocean_park_staging" does not exist
```

Nguyên nhân thường là volume cũ được khởi tạo với `POSTGRES_USER` hoặc `POSTGRES_DB` khác.

Nếu chưa có dữ liệu quan trọng, reset volume staging là cách nhanh nhất.

### 3. Unsafe deployment configuration

Ví dụ:

```text
Unsafe deployment configuration
```

Kiểm tra `.env`:

```env
APP_ENV=staging
JWT_SECRET_KEY=<ít nhất 32 ký tự, không chứa replace/change-me>
ADMIN_PASSWORD=<ít nhất 12 ký tự, không chứa replace/change-me>
AUTO_CREATE_TABLES=false
DATABASE_URL=postgresql+psycopg://...
```

Nếu có khai báo `ADMIN_API_KEY=change-me-in-production`, hãy đổi sang giá trị khác hoặc bỏ dòng đó khỏi `.env`.

### 4. Alembic migration failed

Nếu log báo lỗi khi chạy:

```bash
python -m alembic upgrade head
```

Hãy xem toàn bộ log backend để biết migration fail vì database connection, schema đã tồn tại, hay thiếu dependency.

## Trường hợp backend đã healthy nhưng frontend báo Empty reply

Sau khi sửa `JWT_SECRET_KEY`, staging deploy có thể đi tiếp đến bước:

```text
Container ocean-park-staging-backend-1 Healthy
Checking backend readiness...
{"status":"ready","database":"ok"}
Checking frontend...
curl: (52) Empty reply from server
```

Lúc này backend/database đã ổn. Lỗi còn lại nằm ở bước kiểm tra frontend.

Trong lần chạy thực tế, container frontend mới ở trạng thái:

```text
Up Less than a second
```

nhưng script đã kiểm tra ngay bằng:

```bash
curl -fsSI http://localhost:3000
```

Điều này có thể fail vì Next.js server chưa warm-up xong hoặc phản hồi `HEAD` chưa ổn tại thời điểm vừa start.

Phương án đã áp dụng:

- đổi frontend check từ một lần `curl -I` sang retry loop.
- dùng `GET` nhẹ thay vì `HEAD`.
- nếu frontend vẫn fail sau 30 lần, script tự in log frontend.

Các script đã được cập nhật:

- `scripts/deploy/staging_deploy.sh`
- `scripts/deploy/staging_https_deploy.sh`
- `scripts/deploy/production_deploy.sh`

Sau khi pull code mới trên VPS, chạy lại:

```bash
bash scripts/deploy/staging_deploy.sh
```

Nếu vẫn fail ở frontend, kiểm tra log:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs frontend --tail 100
```

Test thủ công:

```bash
curl -v http://localhost:3000
```

