# DevOps v0.4.0 - Production Docker baseline

## Mục tiêu

Chuẩn hoá Docker cho giai đoạn trước CI/CD và VPS staging:

- Local vẫn chạy được bằng `docker compose up -d --build`.
- Backend có readiness check thật tới database.
- Frontend image nhẹ hơn, chạy theo Next.js standalone output.
- Có compose deploy riêng để dùng trên VPS staging/production.
- Chuẩn bị nền cho bước tiếp theo: CI build image và push registry.

## Công việc đã làm

### Backend

- Thêm endpoint:

```text
GET /ready
```

Endpoint này không chỉ kiểm tra app còn sống, mà còn thử query database bằng `SELECT 1`.

- Docker backend healthcheck chuyển từ `/health` sang `/ready`.
- Dockerfile backend bổ sung:
  - `PYTHONDONTWRITEBYTECODE=1`
  - `PYTHONUNBUFFERED=1`
  - healthcheck dùng `/ready`

Lý do: trong deploy thật, container backend chỉ nên được xem là healthy khi app kết nối được database.

### Frontend

- Chuyển Next.js sang standalone output:

```ts
output: "standalone"
```

- Dockerfile frontend đổi từ:
  - `npm install`
  - copy toàn bộ `.next` và `node_modules`
  - chạy `npm run start`

sang:

  - `npm ci`
  - copy `.next/standalone`
  - copy `.next/static`
  - chạy `node server.js`

Lý do: image production gọn hơn, build ổn định hơn vì dùng lockfile, và runtime ít phụ thuộc hơn vào source tree.

### Compose deploy

Thêm file:

```text
docker-compose.deploy.yml
```

File này dành cho VPS staging/production giai đoạn đầu. Nó vẫn hỗ trợ build trực tiếp từ source trên VPS để bạn dễ học flow:

```bash
git clone -> copy .env -> docker compose build/up
```

Đồng thời file này đã chuẩn bị sẵn `image:` để sau này bước CI/CD có thể đổi sang pull image từ registry như GHCR.

### Environment templates

Cập nhật:

```text
.env.staging.example
.env.production.example
```

Điểm quan trọng: `DATABASE_URL` không còn chứa password trực tiếp. Password được truyền bằng `PGPASSWORD` ở Compose để tránh lỗi khi password có ký tự đặc biệt như `@`, `#`, `/`, `:`.

## Phương án triển khai VPS staging hiện tại

Ở giai đoạn học/demo, VPS có thể build image trực tiếp từ source:

```bash
ssh user@your-vps-ip
git clone <repo-url>
cd C2-App-005
cp .env.staging.example .env
nano .env
docker compose -f docker-compose.deploy.yml up -d --build
```

Sau khi có CI/CD ở v0.5.0, flow sẽ đổi thành:

```bash
docker compose -f docker-compose.deploy.yml pull
docker compose -f docker-compose.deploy.yml up -d
```

Tức VPS không cần tự build nữa, chỉ pull image đã được GitHub Actions build và kiểm tra.

## Cách sử dụng local

Chạy local như cũ:

```powershell
docker compose up -d --build
```

Kiểm tra trạng thái:

```powershell
docker compose ps
```

Kiểm tra backend ready:

```powershell
Invoke-WebRequest -Uri http://localhost:8000/ready -UseBasicParsing
```

Kết quả mong đợi:

```json
{"status":"ready","database":"ok"}
```

Kiểm tra frontend:

```powershell
Invoke-WebRequest -Uri http://localhost:3000/ -UseBasicParsing
```

Kết quả mong đợi: HTTP `200`.

## Cách test đã thực hiện

Backend test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Kết quả:

```text
23 passed
```

Frontend build:

```powershell
cd FE
npm run build
```

Kết quả:

```text
Compiled successfully
```

Compose local config:

```powershell
docker compose config --quiet
```

Kết quả: hợp lệ.

Compose deploy config:

```powershell
docker compose --env-file .env.staging.example -f docker-compose.deploy.yml config --quiet
```

Kết quả: hợp lệ.

Runtime Docker:

```powershell
docker compose up -d
docker compose ps
```

Kết quả:

```text
backend   healthy
database  healthy
frontend  running
```

## Lưu ý

- `docker-compose.deploy.yml` hiện vẫn expose `BACKEND_PORT` và `FRONTEND_PORT` để dễ test trên VPS.
- Ở bước Cloudflare/HTTPS sau này, nên đặt reverse proxy ở trước frontend/backend và hạn chế expose trực tiếp backend ra internet.
- Production thật không nên build trực tiếp trên VPS lâu dài; bước v0.5.0 sẽ chuyển sang GitHub Actions build image.

