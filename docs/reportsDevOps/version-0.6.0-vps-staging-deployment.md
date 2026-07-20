# DevOps v0.6.0 - VPS staging deployment

## Mục tiêu

Chuẩn bị quy trình deploy staging lên VPS theo hướng:

```text
GitHub Actions build image -> GHCR -> VPS pull image -> Docker Compose up
```

Mục tiêu của version này chưa phải production HTTPS hoàn chỉnh, mà là làm cho staging có thể chạy ổn định trên VPS để demo với mentor.

## Công việc đã làm

### 1. Thêm tài liệu deploy staging VPS

File mới:

```text
docs/deployment/staging-vps.md
```

Tài liệu hướng dẫn:

- SSH vào VPS.
- Tạo thư mục `/opt/ocean-park-advisor`.
- Clone repo.
- Tạo `.env` từ `.env.staging.example`.
- Login GHCR nếu image private.
- Chạy deploy staging.
- Kiểm tra container, backend `/ready`, frontend HTTP.
- Xem log và dừng staging an toàn.

### 2. Thêm script kiểm tra VPS

File mới:

```text
scripts/deploy/check_vps_prerequisites.sh
```

Script kiểm tra:

- `docker`
- `docker compose`
- `git`
- `curl`
- quyền truy cập Docker daemon

Nếu thiếu điều kiện nào, script dừng và báo lỗi rõ ràng.

### 3. Thêm script deploy staging

File mới:

```text
scripts/deploy/staging_deploy.sh
```

Script thực hiện:

- kiểm tra đang đứng ở project root
- kiểm tra `.env`
- kiểm tra các biến staging bắt buộc
- chặn placeholder như `replace-with`, `example.com`, `your-repo`
- validate compose config
- pull image từ GHCR
- chạy Docker Compose
- kiểm tra backend readiness
- kiểm tra frontend HTTP

Lệnh chạy trên VPS:

```bash
bash scripts/deploy/staging_deploy.sh
```

### 4. Cập nhật environment templates

Cập nhật:

```text
.env.staging.example
.env.production.example
```

Thêm:

```env
PROJECT_NAME=ocean-park-staging
```

Production image tag được cập nhật lên `v0.6.0` để đồng bộ version.

### 5. Bump version

Cập nhật version:

- backend/project: `0.6.0`
- frontend package: `0.6.0`
- frontend lockfile: `0.6.0`

## Phương án áp dụng

Mình chọn tách staging deployment thành 2 lớp:

### Lớp 1: Compose runtime

Vẫn dùng:

```text
docker-compose.registry.yml
```

File này pull image từ GHCR, không build source trên VPS.

### Lớp 2: Deploy script

Dùng:

```text
scripts/deploy/staging_deploy.sh
```

Script này đóng vai trò "manual CD" giai đoạn đầu. Bạn vẫn SSH vào VPS và tự chạy script, nhưng các bước quan trọng đã được chuẩn hoá.

Sau này ở bản nâng cao, GitHub Actions có thể SSH vào VPS và gọi script này tự động.

## Cách sử dụng trên VPS staging

### Chuẩn bị lần đầu

```bash
ssh user@your-vps-ip
sudo mkdir -p /opt/ocean-park-advisor
sudo chown -R "$USER":"$USER" /opt/ocean-park-advisor
cd /opt/ocean-park-advisor
git clone <repo-url> .
cp .env.staging.example .env
nano .env
```

Trong `.env`, thay tối thiểu:

```env
POSTGRES_PASSWORD=<strong-staging-db-password>
JWT_SECRET_KEY=<at-least-32-random-characters>
ADMIN_EMAIL=<your-admin-email>
ADMIN_PASSWORD=<strong-admin-password>
CORS_ORIGINS=https://staging.your-domain.com
NEXT_PUBLIC_API_URL=https://api-staging.your-domain.com/api/v1
BACKEND_IMAGE=ghcr.io/<owner>/<repo>-backend:dev
FRONTEND_IMAGE=ghcr.io/<owner>/<repo>-frontend:dev
```

Nếu GHCR package private:

```bash
echo "<github-token>" | docker login ghcr.io -u <github-username> --password-stdin
```

Deploy:

```bash
bash scripts/deploy/staging_deploy.sh
```

## Cách test staging trên VPS

Kiểm tra container:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml ps
```

Kiểm tra backend:

```bash
curl http://localhost:8000/ready
```

Kết quả mong đợi:

```json
{"status":"ready","database":"ok"}
```

Kiểm tra frontend:

```bash
curl -I http://localhost:3000
```

Kết quả mong đợi: HTTP `200`.

## Cách update staging sau khi có image mới

```bash
cd /opt/ocean-park-advisor
git pull
bash scripts/deploy/staging_deploy.sh
```

## Cách xem log

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs backend --tail 100
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs frontend --tail 100
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs database --tail 100
```

## Cách test đã thực hiện local

Backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Kết quả:

```text
23 passed
```

Ruff:

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests
```

Kết quả:

```text
All checks passed!
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

Compose registry staging:

```powershell
docker compose --env-file .env.staging.example -f docker-compose.registry.yml config --quiet
```

Kết quả: hợp lệ.

Compose registry production:

```powershell
docker compose --env-file .env.production.example -f docker-compose.registry.yml config --quiet
```

Kết quả: hợp lệ.

## Lưu ý

- Máy Windows local hiện chưa có WSL distro, nên chưa chạy được `bash -n` để kiểm tra script bash trực tiếp tại local.
- Khi lên VPS Linux, nên chạy:

```bash
bash -n scripts/deploy/check_vps_prerequisites.sh
bash -n scripts/deploy/staging_deploy.sh
```

- Docker installation nên làm theo Docker docs chính thức cho Ubuntu, đặc biệt là cài Docker Engine từ apt repository và cài `docker-compose-plugin`.

## Bước tiếp theo

DevOps v0.7.0 sẽ tập trung vào Cloudflare và HTTPS:

- DNS record cho staging.
- Reverse proxy.
- SSL/TLS.
- Hạn chế expose backend trực tiếp ra internet.
