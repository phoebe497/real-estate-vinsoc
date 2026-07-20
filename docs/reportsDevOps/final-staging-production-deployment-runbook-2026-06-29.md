# Final Runbook: Deploy Staging và Production trên VPS

Ngày tạo: 2026-06-29  
Trạng thái: tài liệu chuẩn cuối cùng cho quy trình deploy hiện tại  
Stack hiện tại: GitHub Actions + GHCR + Docker Compose + Nginx host + Certbot  

## 1. Kết luận kiến trúc hiện tại

Dự án hiện đang deploy theo hướng:

```text
GitHub Actions build image
  -> push image lên GitHub Container Registry, viết tắt là GHCR
  -> VPS pull image
  -> Docker Compose chạy container
  -> Nginx host reverse proxy domain vào container
```

Hiện tại **không dùng Caddy cho VPS này** vì VPS đã dùng Nginx + Certbot để giữ port `80/443`.

File compose chuẩn cho staging và production hiện tại là:

```text
docker-compose.registry.yml
```

Không dùng mặc định:

```text
docker-compose.yml
```

cho staging/production, vì file đó là local development compose và hardcode port `3000/8000`.

## 2. Phân loại các file Docker Compose

| File | Mục đích | Có nên dùng cho staging/production hiện tại? |
|---|---|---|
| `docker-compose.yml` | Local development, build trực tiếp từ source, hardcode `3000/8000` | Không |
| `docker-compose.deploy.yml` | Build trực tiếp trên VPS từ source, có biến port | Chỉ dùng dự phòng |
| `docker-compose.registry.yml` | Pull image từ GHCR, có biến port | Có, đây là file chuẩn hiện tại |
| `docker-compose.https.yml` | Dùng Caddy container để tự giữ `80/443` | Không dùng trên VPS hiện tại vì đã có Nginx |

## 3. Mô hình môi trường

| Thành phần | Staging | Production |
|---|---|---|
| Domain | `staging.c2-app-005.quangtm.site` | `c2-app-005.quangtm.site` |
| VPS folder | `/opt/ocean-park-advisor` | `/opt/ocean-park-production` |
| Git branch | `dev` | `main` |
| Docker project | `ocean-park-staging` | `ocean-park-production` |
| Compose file | `docker-compose.registry.yml` | `docker-compose.registry.yml` |
| Frontend host port | `3000` | `3001` |
| Backend host port | `8000` | `8001` |
| Frontend container port | `3000` | `3000` |
| Backend container port | `8000` | `8000` |
| Image tag | `:dev` | `:main` |
| Database | `ocean_park_staging` | `ocean_park_production` |
| Mục đích | Test code mới | Bản ổn định để demo/nộp |

## 4. Luồng Git hiện tại

Quy trình làm việc hiện tại:

```text
TranMinhQuang
  -> Pull Request vào dev
  -> merge dev
  -> GitHub Actions build image :dev
  -> deploy staging
  -> test staging
  -> Pull Request dev vào main
  -> merge main
  -> GitHub Actions build image :main
  -> deploy production
```

Vì production hiện tại chọn dùng thẳng image `:main`, nên **main là nguồn production**. Chỉ merge vào `main` khi staging đã test ổn.

## 5. GitHub Actions và GHCR

Workflow chính:

```text
.github/workflows/ci.yml
```

Workflow hiện có 3 nhóm việc:

1. Backend checks:
   - cài dependency Python
   - chạy Ruff
   - chạy Pytest

2. Frontend build:
   - cài Node.js
   - `npm ci`
   - `npm run build`

3. Docker build and publish:
   - build backend image
   - build frontend image
   - push lên GHCR
   - tạo tag theo branch, ví dụ `dev`, `main`
   - tạo tag theo commit SHA
   - tạo tag theo git tag nếu sau này dùng release version

Image hiện tại dùng:

```env
ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:main
ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:main
```

## 6. Chuẩn bị VPS lần đầu

Trên VPS cần có:

```bash
docker --version
docker compose version
git --version
nginx -v
certbot --version
```

Nếu thiếu Certbot:

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

Nếu repo private, VPS nên clone bằng SSH:

```bash
ssh -T git@github.com
```

Kết quả đúng:

```text
Hi <github-username>! You've successfully authenticated, but GitHub does not provide shell access.
```

## 7. Deploy staging lần đầu

### 7.1 Clone code staging

```bash
cd /opt
git clone git@github.com:AI20K-Build-Cohort-2/C2-App-005.git ocean-park-advisor
cd /opt/ocean-park-advisor
git checkout dev
git pull origin dev
```

### 7.2 Tạo file `.env` staging

```bash
cp .env.staging.example .env
nano .env
```

Các biến staging quan trọng:

```env
APP_ENV=staging
PROJECT_NAME=ocean-park-staging

POSTGRES_DB=ocean_park_staging
POSTGRES_USER=ocean_staging
POSTGRES_PASSWORD=<staging_db_password>
DATABASE_URL=postgresql+psycopg://ocean_staging:<staging_db_password>@database:5432/ocean_park_staging

JWT_SECRET_KEY=<staging_jwt_secret_32_chars_or_more>
ADMIN_EMAIL=<staging_admin_email>
ADMIN_PASSWORD=<staging_admin_password_12_chars_or_more>
ADMIN_FULL_NAME=Staging Administrator

CORS_ORIGINS=https://staging.c2-app-005.quangtm.site
NEXT_PUBLIC_API_URL=https://staging.c2-app-005.quangtm.site/api/v1

FRONTEND_PORT=3000
BACKEND_PORT=8000

BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev

FRONTEND_DOMAIN=staging.c2-app-005.quangtm.site
API_DOMAIN=staging.c2-app-005.quangtm.site

LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=<openrouter_key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-chat
OPENROUTER_SITE_URL=https://staging.c2-app-005.quangtm.site
OPENROUTER_APP_NAME=Ocean Park AI Advisor
```

Không để API URL dạng:

```text
https://staging.c2-app-005.quangtm.site:8000/api/v1
```

Backend port `8000` chỉ là HTTP nội bộ trên VPS, không phải HTTPS public.

### 7.3 Deploy staging

Script staging đã có sẵn và đúng với cấu trúc hiện tại:

```bash
cd /opt/ocean-park-advisor
bash scripts/deploy/staging_deploy.sh
```

Script này mặc định dùng:

```bash
PROJECT_NAME=ocean-park-staging
COMPOSE_FILE=docker-compose.registry.yml
ENV_FILE=.env
BACKEND_READY_URL=http://localhost:8000/ready
FRONTEND_URL=http://localhost:3000
```

### 7.4 Kiểm tra staging container

```bash
docker compose --env-file .env \
  -p ocean-park-staging \
  -f docker-compose.registry.yml \
  ps
```

Kỳ vọng:

```text
database  healthy
backend   healthy
frontend  up/started
```

Test nội bộ:

```bash
curl http://127.0.0.1:8000/ready
curl -I http://127.0.0.1:3000
```

Kỳ vọng backend:

```json
{"status":"ready","database":"ok"}
```

## 8. DNS và Nginx cho staging

DNS record:

```text
Type: A
Name: staging.c2-app-005
Value: 103.149.87.83
```

Test:

```bash
nslookup staging.c2-app-005.quangtm.site
```

Nginx staging mapping:

```nginx
server {
    listen 80;
    server_name staging.c2-app-005.quangtm.site;

    client_max_body_size 20M;

    location /api/v1/ {
        proxy_pass http://127.0.0.1:8000/api/v1/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /agent/ {
        proxy_pass http://127.0.0.1:8000/agent/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /ready {
        proxy_pass http://127.0.0.1:8000/ready;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable và reload:

```bash
sudo ln -s /etc/nginx/sites-available/staging.c2-app-005.quangtm.site /etc/nginx/sites-enabled/staging.c2-app-005.quangtm.site
sudo nginx -t
sudo systemctl reload nginx
```

Cấp HTTPS:

```bash
sudo certbot --nginx -d staging.c2-app-005.quangtm.site
```

Test:

```bash
curl -I https://staging.c2-app-005.quangtm.site
curl https://staging.c2-app-005.quangtm.site/ready
```

## 9. Update staging khi có code mới

Sau khi PR vào `dev` đã merge và GitHub Actions build image `:dev` thành công:

```bash
cd /opt/ocean-park-advisor
git checkout dev
git pull origin dev
bash scripts/deploy/staging_deploy.sh
```

Nếu chỉ muốn pull image mới mà không cần cập nhật source scripts:

```bash
cd /opt/ocean-park-advisor
docker compose --env-file .env \
  -p ocean-park-staging \
  -f docker-compose.registry.yml \
  pull

docker compose --env-file .env \
  -p ocean-park-staging \
  -f docker-compose.registry.yml \
  up -d
```

Khuyến nghị vẫn dùng script staging vì script có kiểm tra env, compose, backend readiness và frontend readiness.

## 10. Deploy production lần đầu

Production hiện tại chọn dùng image tag `:main`, không dùng release tag `v1.0.0` ở giai đoạn này.

### 10.1 Clone code production

```bash
cd /opt
git clone git@github.com:AI20K-Build-Cohort-2/C2-App-005.git ocean-park-production
cd /opt/ocean-park-production
git checkout main
git pull origin main
```

### 10.2 Tạo file `.env` production

```bash
cd /opt/ocean-park-production
cp .env.production.example .env
nano .env
```

Production `.env` quan trọng:

```env
APP_ENV=production
PROJECT_NAME=ocean-park-production

POSTGRES_DB=ocean_park_production
POSTGRES_USER=ocean_production
POSTGRES_PASSWORD=<production_db_password>
DATABASE_URL=postgresql+psycopg://ocean_production:<production_db_password>@database:5432/ocean_park_production

AUTO_CREATE_TABLES=false
AUTO_SEED_CATALOG=true

JWT_SECRET_KEY=<production_jwt_secret_32_chars_or_more>
ACCESS_TOKEN_EXPIRE_MINUTES=120
ADMIN_EMAIL=<production_admin_email>
ADMIN_PASSWORD=<production_admin_password_12_chars_or_more>
ADMIN_FULL_NAME=Production Administrator

CORS_ORIGINS=https://c2-app-005.quangtm.site
NEXT_PUBLIC_API_URL=https://c2-app-005.quangtm.site/api/v1

FRONTEND_PORT=3001
BACKEND_PORT=8001

BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:main
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:main

FRONTEND_DOMAIN=c2-app-005.quangtm.site
API_DOMAIN=c2-app-005.quangtm.site
ACME_EMAIL=<your_email>

LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=<openrouter_key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-chat
OPENROUTER_SITE_URL=https://c2-app-005.quangtm.site
OPENROUTER_APP_NAME=Ocean Park AI Advisor
```

Lưu ý:

- `POSTGRES_PASSWORD` và password trong `DATABASE_URL` phải giống nhau.
- `FRONTEND_DOMAIN` và `API_DOMAIN` phải tách thành hai dòng riêng.
- Không để placeholder `your-repo`, `example.com`, `replace-with`.
- Nếu `OPENROUTER_API_KEY` trống thì web có thể mở được nhưng AI chat sẽ lỗi.

### 10.3 Deploy production bằng registry compose

Không chạy:

```bash
docker compose --env-file .env -p ocean-park-production up -d --build
```

vì lệnh này mặc định dùng `docker-compose.yml` và sẽ đụng port staging.

Lệnh đúng:

```bash
cd /opt/ocean-park-production

docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  config
```

Kiểm tra trong output phải thấy:

```text
published: "8001"
published: "3001"
```

Sau đó chạy:

```bash
docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  up -d
```

Nếu muốn chắc chắn pull image mới trước:

```bash
docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  pull

docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  up -d
```

### 10.4 Kiểm tra production container

```bash
docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  ps
```

Kỳ vọng:

```text
ocean-park-production-database-1  Healthy
ocean-park-production-backend-1   Healthy
ocean-park-production-frontend-1  Started/Up
```

Kiểm tra port:

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

Kỳ vọng:

```text
ocean-park-production-frontend-1   0.0.0.0:3001->3000/tcp
ocean-park-production-backend-1    0.0.0.0:8001->8000/tcp
ocean-park-staging-frontend-1      0.0.0.0:3000->3000/tcp
ocean-park-staging-backend-1       0.0.0.0:8000->8000/tcp
```

Test nội bộ:

```bash
curl http://127.0.0.1:8001/ready
curl -I http://127.0.0.1:3001
```

Kỳ vọng:

```json
{"status":"ready","database":"ok"}
```

Route này có thể trả `404` và không sao:

```bash
curl http://127.0.0.1:8001/api/v1/ready
```

Vì health route hiện tại là:

```text
/ready
```

không phải:

```text
/api/v1/ready
```

## 11. DNS và Nginx cho production

DNS record:

```text
Type: A
Name: c2-app-005
Value: 103.149.87.83
```

Test:

```bash
nslookup c2-app-005.quangtm.site
```

Tạo Nginx site:

```bash
sudo nano /etc/nginx/sites-available/c2-app-005.quangtm.site
```

Nội dung:

```nginx
server {
    listen 80;
    server_name c2-app-005.quangtm.site;

    client_max_body_size 20M;

    location /api/v1/ {
        proxy_pass http://127.0.0.1:8001/api/v1/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /agent/ {
        proxy_pass http://127.0.0.1:8001/agent/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8001/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8001/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /ready {
        proxy_pass http://127.0.0.1:8001/ready;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/c2-app-005.quangtm.site /etc/nginx/sites-enabled/c2-app-005.quangtm.site
sudo nginx -t
sudo systemctl reload nginx
```

Nếu symlink đã tồn tại thì bỏ qua bước `ln -s`.

Test HTTP:

```bash
curl -I http://c2-app-005.quangtm.site
curl http://c2-app-005.quangtm.site/ready
curl -I http://c2-app-005.quangtm.site/docs
```

Cấp HTTPS:

```bash
sudo certbot --nginx -d c2-app-005.quangtm.site
```

Test HTTPS:

```bash
curl -I https://c2-app-005.quangtm.site
curl https://c2-app-005.quangtm.site/ready
```

## 12. Update production khi có code mới vào main

Vì production hiện tại dùng image `:main`, khi có code mới:

1. Merge code vào `main`.
2. Đợi GitHub Actions pass.
3. Đợi Docker build/publish image `:main` xong.
4. SSH vào VPS.
5. Pull image mới và restart production.

Lệnh trên VPS:

```bash
cd /opt/ocean-park-production
git checkout main
git pull origin main

docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  pull

docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  up -d
```

Test sau deploy:

```bash
curl http://127.0.0.1:8001/ready
curl -I http://127.0.0.1:3001
curl -I https://c2-app-005.quangtm.site
```

Checklist browser:

- Trang chủ production load được.
- Login/register user hoạt động.
- Chat AI hoạt động.
- Admin login hoạt động.
- Dashboard admin hoạt động.
- Lead/customer hoạt động.
- DevTools không còn request tới `localhost:8000`, `IP:8000`, hoặc `domain:8000`.

## 13. Khi nào cần `git pull` trên VPS?

Với `docker-compose.registry.yml`, app chạy từ GHCR image nên `git pull` không phải lúc nào cũng bắt buộc.

Tuy nhiên vẫn nên chạy:

```bash
git pull origin main
```

khi:

- `docker-compose.registry.yml` thay đổi.
- script deploy thay đổi.
- docs/env example thay đổi.
- muốn VPS repo theo đúng `main`.

Nếu chỉ có source app thay đổi và image `:main` đã được build/push, phần quan trọng nhất vẫn là:

```bash
docker compose --env-file .env -p ocean-park-production -f docker-compose.registry.yml pull
docker compose --env-file .env -p ocean-park-production -f docker-compose.registry.yml up -d
```

## 14. Xem log

Staging:

```bash
cd /opt/ocean-park-advisor

docker compose --env-file .env \
  -p ocean-park-staging \
  -f docker-compose.registry.yml \
  logs backend --tail 120

docker compose --env-file .env \
  -p ocean-park-staging \
  -f docker-compose.registry.yml \
  logs frontend --tail 120
```

Production:

```bash
cd /opt/ocean-park-production

docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  logs backend --tail 120

docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  logs frontend --tail 120
```

## 15. Backup database

Production nên backup trước các thay đổi lớn.

Chạy:

```bash
cd /opt/ocean-park-production

PROJECT_NAME=ocean-park-production \
COMPOSE_FILE=docker-compose.registry.yml \
ENV_FILE=.env \
bash scripts/deploy/backup_postgres.sh
```

Kiểm tra backup:

```bash
ls -lah backups/postgres
```

Staging nếu cần:

```bash
cd /opt/ocean-park-advisor

PROJECT_NAME=ocean-park-staging \
COMPOSE_FILE=docker-compose.registry.yml \
ENV_FILE=.env \
bash scripts/deploy/backup_postgres.sh
```

## 16. Dừng hoặc restart service

Restart production:

```bash
cd /opt/ocean-park-production
docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  restart
```

Dừng production:

```bash
cd /opt/ocean-park-production
docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  down
```

Lưu ý: `down` không xóa volume database nếu không dùng `-v`. Không chạy `down -v` nếu chưa backup.

## 17. Các lỗi thường gặp

### 17.1 Port already allocated

Lỗi:

```text
Bind for 0.0.0.0:8000 failed: port is already allocated
```

Nguyên nhân thường gặp:

- Đang chạy nhầm `docker-compose.yml`.
- Production cố dùng port staging.

Cách đúng:

```bash
docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  config
```

Phải thấy production dùng:

```text
3001
8001
```

### 17.2 Backend unhealthy

Kiểm tra log:

```bash
docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  logs backend --tail 200
```

Các nguyên nhân từng gặp:

- `JWT_SECRET_KEY` quá ngắn.
- `ADMIN_PASSWORD` dưới 12 ký tự.
- `POSTGRES_PASSWORD` khác password trong `DATABASE_URL`.
- `.env` bị dính 2 biến trên cùng một dòng.
- Image tag sai hoặc không tồn tại.

### 17.3 HTTPS gọi nhầm `:8000`

Triệu chứng:

```text
ERR_SSL_PROTOCOL_ERROR
```

Nguyên nhân:

Frontend gọi:

```text
https://domain:8000/api/v1
```

Trong khi backend port `8000/8001` là HTTP nội bộ, không phải HTTPS public.

Đường đúng:

```text
https://domain/api/v1
```

### 17.4 AI chat lỗi 500

Kiểm tra:

```bash
docker compose --env-file .env \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  logs backend --tail 200
```

Các điểm cần xem:

- `OPENROUTER_API_KEY` có trống không.
- `LLM_PROVIDER=openrouter`.
- model có đúng không.
- backend có ra internet được không.

## 18. Bảo mật

Không commit các file:

```text
.env
.env.local
.env.production
.env.staging
```

Sau khi paste secret vào chat, log, hoặc nơi công khai, nên rotate:

- `OPENROUTER_API_KEY`
- `JWT_SECRET_KEY`
- `ADMIN_PASSWORD`
- `POSTGRES_PASSWORD`

Nếu đổi `ADMIN_PASSWORD` trong `.env` sau khi admin đã được seed, database có thể không tự update password user cũ. Khi đó cần reset password trực tiếp trong database hoặc tạo script quản trị riêng.

## 19. Trạng thái hoàn thành

Staging hoàn thành khi:

- `https://staging.c2-app-005.quangtm.site` mở được.
- `/ready` trả `{"status":"ready","database":"ok"}`.
- Login/register hoạt động.
- Admin hoạt động.
- Chat AI hoạt động.
- Browser không gọi `:8000`.

Production hoàn thành khi:

- `https://c2-app-005.quangtm.site` mở được.
- Production containers dùng project `ocean-park-production`.
- Production ports là `3001/8001`.
- Staging vẫn chạy riêng ở `3000/8000`.
- Production dùng image `:main`.
- Chức năng user/admin/chat hoạt động.
- Nginx route đúng `/`, `/api/v1`, `/agent`, `/docs`, `/openapi.json`, `/ready`.

## 20. Hướng nâng cấp CD sau này

Hiện tại deploy vẫn là manual CD:

```text
GitHub Actions build image
  -> user SSH vào VPS
  -> pull image
  -> up -d
```

Hướng CD sau này:

### Staging CD

Trigger:

```text
push/merge vào dev
```

Action:

```bash
cd /opt/ocean-park-advisor
git pull origin dev
bash scripts/deploy/staging_deploy.sh
```

### Production CD

Vì hiện tại production dùng `:main`, trigger có thể là:

```text
push/merge vào main
```

Action:

```bash
cd /opt/ocean-park-production
git pull origin main
docker compose --env-file .env -p ocean-park-production -f docker-compose.registry.yml pull
docker compose --env-file .env -p ocean-park-production -f docker-compose.registry.yml up -d
```

Sau này nếu muốn production an toàn hơn, có thể chuyển từ `:main` sang release tag:

```text
v1.0.0
v1.0.1
v1.0.2
```

Khi đó production deploy sẽ chỉ chạy khi push tag release.

