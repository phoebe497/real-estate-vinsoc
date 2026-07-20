# Staging VPS deployment guide

Tài liệu này mô tả flow staging trước khi lên production thật.

## Mục tiêu staging

Staging là môi trường để bạn demo với mentor và kiểm thử trước production.

Flow mong muốn:

```text
GitHub Actions -> GHCR images -> VPS pulls images -> Docker Compose starts app
```

Ở v0.6.0, VPS không cần build source nữa nếu bạn dùng `docker-compose.registry.yml`.

## Yêu cầu VPS

Khuyến nghị tối thiểu:

- Ubuntu 22.04 LTS hoặc 24.04 LTS.
- RAM 2GB trở lên.
- Disk 25GB trở lên.
- SSH access.
- Docker Engine và Docker Compose plugin.

Theo Docker docs, trên Ubuntu nên cài Docker Engine từ Docker apt repository và cài kèm:

```text
docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Chuẩn bị lần đầu trên VPS

### 1. SSH vào VPS

```bash
ssh user@your-vps-ip
```

### 2. Tạo thư mục app

```bash
sudo mkdir -p /opt/ocean-park-advisor
sudo chown -R "$USER":"$USER" /opt/ocean-park-advisor
cd /opt/ocean-park-advisor
```

### 3. Clone repo

```bash
git clone <repo-url> .
```

Nếu VPS chỉ pull image từ registry, repo chủ yếu dùng để lưu compose files, env template và deploy scripts.

### 4. Tạo file `.env`

```bash
cp .env.staging.example .env
nano .env
```

Cần thay tối thiểu:

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

Nếu chưa có domain/Cloudflare, có thể tạm test bằng IP và port:

```env
CORS_ORIGINS=http://your-vps-ip:3000
NEXT_PUBLIC_API_URL=http://your-vps-ip:8000/api/v1
```

## Login GHCR nếu package private

Nếu image GHCR là private, VPS cần login:

```bash
echo "<github-token>" | docker login ghcr.io -u <github-username> --password-stdin
```

Token chỉ nên có quyền đọc package. Không commit token vào repo.

## Deploy staging

Chạy script:

```bash
bash scripts/deploy/staging_deploy.sh
```

Script sẽ:

- kiểm tra Docker/Compose
- validate `.env`
- pull backend/frontend image
- chạy `docker compose up -d`
- kiểm tra container status
- gọi `/ready`

Nếu đã có domain và muốn chạy qua HTTPS/Caddy, dùng:

```bash
bash scripts/deploy/staging_https_deploy.sh
```

Xem thêm:

```text
docs/deployment/cloudflare-https.md
```

## Kiểm tra thủ công

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml ps
curl http://localhost:8000/ready
curl -I http://localhost:3000
```

Kết quả mong đợi:

```json
{"status":"ready","database":"ok"}
```

Frontend trả HTTP `200`.

## Update staging khi có image mới

Sau khi push `dev` và GitHub Actions build image mới:

```bash
cd /opt/ocean-park-advisor
git pull
bash scripts/deploy/staging_deploy.sh
```

## Xem log

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs backend --tail 100
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs frontend --tail 100
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs database --tail 100
```

## Dừng staging

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml down
```

Không thêm `-v` nếu bạn muốn giữ database volume.
