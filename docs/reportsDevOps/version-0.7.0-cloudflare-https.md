# DevOps v0.7.0 - Cloudflare, HTTPS and reverse proxy

## Mục tiêu

Chuẩn bị cấu hình để staging/production chạy qua domain thật và HTTPS:

```text
Browser -> Cloudflare -> VPS :80/:443 -> Caddy -> frontend/backend
```

Điểm quan trọng của version này:

- Chỉ Caddy expose port public `80/443`.
- Backend/frontend không expose trực tiếp ra internet.
- Caddy tự reverse proxy:
  - frontend domain -> frontend container
  - API domain -> backend container
- Chuẩn bị hướng dẫn Cloudflare DNS và SSL/TLS mode.

## Công việc đã làm

### 1. Thêm Caddy reverse proxy config

File mới:

```text
deploy/caddy/Caddyfile
```

Config gồm 2 domain:

```text
FRONTEND_DOMAIN -> frontend:3000
API_DOMAIN      -> backend:8000
```

Caddy cũng thêm một số security headers cơ bản:

- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `Referrer-Policy`

### 2. Thêm Docker Compose HTTPS runtime

File mới:

```text
docker-compose.https.yml
```

File này chạy:

- `database`
- `backend`
- `frontend`
- `caddy`

Khác với `docker-compose.registry.yml`, file HTTPS không publish:

```text
backend:8000
frontend:3000
database:5432
```

Chỉ publish:

```text
80/tcp
443/tcp
443/udp
```

### 3. Thêm script deploy HTTPS staging

File mới:

```text
scripts/deploy/staging_https_deploy.sh
```

Script thực hiện:

- kiểm tra VPS prerequisites
- kiểm tra `.env`
- yêu cầu thêm:
  - `FRONTEND_DOMAIN`
  - `API_DOMAIN`
  - `ACME_EMAIL`
- validate compose config
- pull image từ GHCR
- chạy Docker Compose HTTPS
- kiểm tra backend qua HTTPS `/ready`
- kiểm tra frontend qua HTTPS

### 4. Thêm tài liệu Cloudflare/HTTPS

File mới:

```text
docs/deployment/cloudflare-https.md
```

Tài liệu hướng dẫn:

- tạo DNS records trên Cloudflare
- nên bắt đầu bằng DNS Only để Caddy lấy cert dễ hơn
- sau khi HTTPS ổn thì bật Proxied nếu muốn
- đặt SSL/TLS mode là Full strict
- mở firewall `80/443`
- không mở public `3000/8000/5432`

### 5. Cập nhật staging VPS guide

File cập nhật:

```text
docs/deployment/staging-vps.md
```

Thêm nhánh deploy HTTPS:

```bash
bash scripts/deploy/staging_https_deploy.sh
```

### 6. Cập nhật environment templates

Cập nhật:

```text
.env.staging.example
.env.production.example
```

Thêm:

```env
FRONTEND_DOMAIN=staging.example.com
API_DOMAIN=api-staging.example.com
ACME_EMAIL=admin@example.com
```

### 7. Bump version

Cập nhật version:

- backend/project: `0.7.0`
- frontend package: `0.7.0`
- frontend lockfile: `0.7.0`

## Phương án áp dụng

Mình chọn Caddy thay vì Nginx ở giai đoạn này vì:

- Caddyfile ngắn, dễ đọc.
- Caddy tự động quản lý HTTPS khi domain trỏ đúng về server.
- Phù hợp với VPS staging nhỏ và workflow học/deploy nhanh.

Theo Caddy documentation, automatic HTTPS cần DNS trỏ về server, port `80/443` mở, Caddy có domain trong config và storage certificate được persist. Vì vậy `docker-compose.https.yml` có volume:

```text
caddy_data
caddy_config
```

để giữ certificate qua các lần restart.

Với Cloudflare, hướng dẫn khuyến nghị SSL/TLS mode:

```text
Full (strict)
```

vì mode này kiểm tra origin certificate hợp lệ.

## Cách dùng trên VPS staging

### 1. Chuẩn bị DNS

Trong Cloudflare DNS:

| Type | Name | Target |
| --- | --- | --- |
| A | staging | VPS public IP |
| A | api-staging | VPS public IP |

Ban đầu nên để DNS Only.

### 2. Chuẩn bị `.env`

```bash
cd /opt/ocean-park-advisor
cp .env.staging.example .env
nano .env
```

Thay các giá trị:

```env
CORS_ORIGINS=https://staging.your-domain.com
NEXT_PUBLIC_API_URL=https://api-staging.your-domain.com/api/v1
FRONTEND_DOMAIN=staging.your-domain.com
API_DOMAIN=api-staging.your-domain.com
ACME_EMAIL=admin@your-domain.com
BACKEND_IMAGE=ghcr.io/<owner>/<repo>-backend:dev
FRONTEND_IMAGE=ghcr.io/<owner>/<repo>-frontend:dev
```

### 3. Deploy HTTPS

```bash
bash scripts/deploy/staging_https_deploy.sh
```

### 4. Kiểm tra

```bash
curl https://api-staging.your-domain.com/ready
curl -I https://staging.your-domain.com
docker compose --env-file .env -p ocean-park-staging -f docker-compose.https.yml ps
```

Kết quả backend mong đợi:

```json
{"status":"ready","database":"ok"}
```

### 5. Bật Cloudflare Proxied

Sau khi HTTPS hoạt động trực tiếp, có thể bật Proxied trên Cloudflare và đặt SSL/TLS mode:

```text
Full (strict)
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

Compose HTTPS staging:

```powershell
docker compose --env-file .env.staging.example -f docker-compose.https.yml config --quiet
```

Kết quả: hợp lệ.

Compose HTTPS production:

```powershell
docker compose --env-file .env.production.example -f docker-compose.https.yml config --quiet
```

Kết quả: hợp lệ.

Caddyfile validation:

```powershell
docker run --rm -v "${PWD}/deploy/caddy/Caddyfile:/etc/caddy/Caddyfile:ro" `
  -e ACME_EMAIL=admin@example.com `
  -e FRONTEND_DOMAIN=staging.example.com `
  -e API_DOMAIN=api-staging.example.com `
  caddy:2-alpine caddy validate --config /etc/caddy/Caddyfile
```

Kết quả:

```text
Valid configuration
```

## Lưu ý

- Version này chuẩn bị cấu hình Cloudflare/HTTPS, chưa thao tác trực tiếp trên Cloudflare hay VPS thật.
- Khi test certificate thật, VPS cần mở port `80/443`.
- Nếu Cloudflare Proxied gây khó khăn lúc cấp certificate lần đầu, chuyển record sang DNS Only trước, deploy HTTPS thành công rồi bật Proxied lại.
- Không dùng `docker compose down -v` nếu muốn giữ database và certificate volumes.

## Nguồn tham khảo

- Caddy Automatic HTTPS: https://caddyserver.com/docs/automatic-https
- Caddy reverse_proxy directive: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- Cloudflare Full strict mode: https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/
- Cloudflare proxied DNS records: https://developers.cloudflare.com/dns/proxy-status/

## Bước tiếp theo

DevOps v0.8.0 sẽ tập trung vào production release, backup và rollback:

- versioned release tag
- backup PostgreSQL
- restore drill
- rollback image tag
- checklist trước production
