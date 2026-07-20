# Kế hoạch deploy production sau khi đã có staging

Ngày lập kế hoạch: 2026-06-29  
Trạng thái: Chờ duyệt trước khi thực hiện  
Staging hiện tại: `https://staging.c2-app-005.quangtm.site`  
Vấn đề hiện tại: `dev` và `main` đang cách nhau xa, link staging đã nộp nhưng vẫn có thể thay đổi nếu tiếp tục deploy từ `dev`

Quyết định cập nhật: vì hiện tại còn đủ thời gian phát triển, production workflow sẽ đi theo hướng sạch nhất: **đưa `dev` về `main` bằng Pull Request có kiểm soát, tag release từ `main`, rồi deploy production từ release tag**. Không deploy production từ branch tắt nếu chưa cần gấp.

## 1. Bối cảnh

Hiện tại dự án đã có staging online:

```text
https://staging.c2-app-005.quangtm.site
```

Staging đang chạy trên VPS qua:

```text
DNS → VPS → Nginx host → Docker containers
```

Nếu tiếp tục phát triển trên `dev` và redeploy staging, link staging đã nộp có thể thay đổi hoặc tạm lỗi. Vì vậy cần có production riêng để giữ bản ổn định.

## 2. Mục tiêu production

Tạo một môi trường production riêng, ổn định, không bị ảnh hưởng bởi deploy staging.

Production nên có:

- Domain riêng.
- Docker project riêng.
- Database volume riêng.
- `.env.production` riêng.
- Backend/frontend port nội bộ riêng.
- Nginx server block riêng.
- Image tag cố định, không phụ thuộc `dev` rolling tag.

Mục tiêu sau khi hoàn thành:

```text
Staging  → dùng để test code mới
Production → dùng để nộp/demo bản ổn định
```

## 3. Domain production đề xuất

Có 2 lựa chọn:

### Lựa chọn A

```text
https://c2-app-005.quangtm.site
```

Ưu điểm:

- Ngắn.
- Đẹp.
- Phù hợp để nộp mentor.

### Lựa chọn B

```text
https://prod.c2-app-005.quangtm.site
```

Ưu điểm:

- Rõ đây là production.
- Tách biệt với staging bằng prefix.

Đề xuất của tôi:

```text
https://c2-app-005.quangtm.site
```

Staging giữ:

```text
https://staging.c2-app-005.quangtm.site
```

## 4. Kiến trúc production đề xuất

Vì VPS hiện đã dùng Nginx host để phục vụ staging, production cũng nên dùng Nginx host, không dùng Caddy trong Docker.

Lý do:

- `docker-compose.https.yml` hiện có service `caddy` bind port `80/443`.
- Nginx trên VPS cũng đang bind `80/443`.
- Nếu chạy Caddy production cùng VPS sẽ đụng port.
- Dùng Nginx host cho cả staging/production sẽ đơn giản và nhất quán hơn.

Kiến trúc:

```text
User / Mentor
  ↓
https://c2-app-005.quangtm.site
  ↓
Nginx host trên VPS
  ├── /        → production frontend:3001
  ├── /api/v1  → production backend:8001/api/v1
  ├── /agent   → production backend:8001/agent
  ├── /docs    → production backend:8001/docs
  └── /openapi.json → production backend:8001/openapi.json
```

Staging vẫn giữ:

```text
https://staging.c2-app-005.quangtm.site
  ├── frontend:3000
  └── backend:8000
```

Production dùng port khác để không đụng staging:

```text
FRONTEND_PORT=3001
BACKEND_PORT=8001
PROJECT_NAME=ocean-park-production
```

## 5. Tách biệt staging và production

| Thành phần | Staging | Production |
|---|---|---|
| Domain | `staging.c2-app-005.quangtm.site` | `c2-app-005.quangtm.site` |
| Docker project | `ocean-park-staging` | `ocean-park-production` |
| Frontend port | `3000` | `3001` |
| Backend port | `8000` | `8001` |
| Database volume | staging volume | production volume riêng |
| Env file | `.env` hoặc `.env.staging` | `.env.production` |
| Image tag | `:dev` | release tag, ví dụ `:v1.0.0` |
| Mục đích | test thay đổi mới | bản ổn định để nộp/demo |

## 6. Vấn đề dev và main đang cách nhau xa

Hiện tại `dev` và `main` lệch xa, nên không nên deploy production trực tiếp từ `main` ngay nếu `main` chưa có code mới.

Vì còn đủ thời gian, chọn workflow sạch:

```text
dev ổn định trên staging
  ↓
Tạo Pull Request dev → main
  ↓
Resolve conflict kỹ
  ↓
CI pass
  ↓
Review lại diff quan trọng
  ↓
Merge vào main
  ↓
Tag release từ main
  ↓
GitHub Actions build image theo tag
  ↓
Deploy production bằng image tag cố định
```

Lý do chọn hướng này:

- `main` luôn phản ánh bản production.
- Dễ giải thích với mentor/team.
- Không tạo production từ một branch chưa được hợp nhất.
- Lịch sử Git sạch hơn.
- Sau này setup automated production CD dễ hơn.
- Rollback/release theo tag rõ ràng.

### Vì sao không chọn release branch tắt từ dev?

Hướng tạo `release/v1.0.0` từ `dev` rồi deploy production trước chỉ phù hợp khi cần có production rất gấp. Hiện tại bạn còn thời gian, nên không cần đi đường tắt này.

Nhược điểm nếu đi đường tắt:

- `main` không phản ánh production ngay.
- Team dễ nhầm production đang chạy code nào.
- Sau đó vẫn phải xử lý merge về main.
- Dễ phát sinh lệch branch lâu dài.

Vì vậy kế hoạch mới là:

```text
dev → PR → main → tag → production
```

## 7. Production release workflow sạch

Quy trình:

```text
dev hiện tại
  ↓
Tạo PR dev → main
  ↓
Resolve conflict nếu có
  ↓
CI pass
  ↓
Merge main
  ↓
Tag release từ main
  ↓
Build image tag release
  ↓
Deploy production bằng tag đó
```

Ưu điểm:

- Đúng Git flow.
- Production lấy từ `main`.
- Dễ giải thích với mentor.

Nhược điểm:

- Nếu dev/main lệch quá xa, merge có thể cần xử lý conflict kỹ.

## 8. Production image tag

Không nên dùng:

```text
FRONTEND_IMAGE=...:dev
BACKEND_IMAGE=...:dev
```

cho production.

Nên dùng tag cố định:

```text
BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:v1.0.0
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:v1.0.0
```

Lý do:

- `:dev` thay đổi mỗi lần merge dev.
- `:v1.0.0` cố định, production không tự đổi.
- Rollback dễ hơn.

## 9. DNS production

Nếu chọn domain:

```text
c2-app-005.quangtm.site
```

Tạo DNS record:

```text
Type: A
Name: c2-app-005
Value: 103.149.87.83
```

Kiểm tra:

```bash
nslookup c2-app-005.quangtm.site
```

Kỳ vọng:

```text
Address: 103.149.87.83
```

## 10. Nginx production server block

Tạo file:

```text
/etc/nginx/sites-available/c2-app-005.quangtm.site
```

Mapping:

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
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8001/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

## 11. HTTPS production

Sau khi HTTP domain chạy:

```bash
sudo certbot --nginx -d c2-app-005.quangtm.site
```

Test:

```bash
curl -I https://c2-app-005.quangtm.site
```

## 12. Production env đề xuất

Tạo:

```text
.env.production
```

Các biến quan trọng:

```env
APP_ENV=production
LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=8000

POSTGRES_DB=ocean_park_production
POSTGRES_USER=ocean_production
POSTGRES_PASSWORD=<strong-production-db-password>
DATABASE_URL=postgresql+psycopg://ocean_production:<strong-production-db-password>@database:5432/ocean_park_production
AUTO_CREATE_TABLES=false
AUTO_SEED_CATALOG=true

JWT_SECRET_KEY=<unique-32+-chars-production-secret>
ACCESS_TOKEN_EXPIRE_MINUTES=480
ADMIN_EMAIL=<production-admin-email>
ADMIN_PASSWORD=<strong-admin-password-12+-chars>
ADMIN_FULL_NAME=Production Administrator

CORS_ORIGINS=https://c2-app-005.quangtm.site
NEXT_PUBLIC_API_URL=https://c2-app-005.quangtm.site/api/v1

FRONTEND_PORT=3001
BACKEND_PORT=8001
PROJECT_NAME=ocean-park-production

BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:v1.0.0
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:v1.0.0

FRONTEND_DOMAIN=c2-app-005.quangtm.site
API_DOMAIN=c2-app-005.quangtm.site
ACME_EMAIL=<your-email>

LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=<new-production-openrouter-key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
OPENROUTER_SITE_URL=https://c2-app-005.quangtm.site
OPENROUTER_APP_NAME=Ocean Park AI Advisor
```

Không dùng lại secret staging nếu muốn production sạch.

## 13. Compose production đề xuất

Không nên dùng `docker-compose.https.yml` trên cùng VPS hiện tại vì file đó chạy Caddy và bind port `80/443`.

Nên dùng một compose kiểu registry nhưng với env production:

```bash
docker compose --env-file .env.production \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  up -d
```

Với:

```env
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

Như vậy staging và production chạy song song trên cùng VPS:

```text
staging frontend:3000
staging backend:8000
production frontend:3001
production backend:8001
```

## 14. Deploy production thủ công lần đầu

Trên VPS:

```bash
cd /opt/ocean-park-advisor
cp .env.production.example .env.production
nano .env.production
```

Validate compose:

```bash
docker compose --env-file .env.production \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  config --quiet
```

Pull images:

```bash
docker compose --env-file .env.production \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  pull
```

Start:

```bash
docker compose --env-file .env.production \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  up -d
```

Check:

```bash
docker compose --env-file .env.production \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  ps
```

Test local VPS:

```bash
curl http://localhost:8001/ready
curl -I http://localhost:3001
```

Test domain:

```bash
curl -I http://c2-app-005.quangtm.site
curl http://c2-app-005.quangtm.site/docs
```

Sau đó cấp HTTPS:

```bash
sudo certbot --nginx -d c2-app-005.quangtm.site
```

## 15. Chuẩn hóa `dev → main` trước khi production

Vì chọn workflow sạch, cần đưa code từ `dev` về `main` trước khi production.

### Bước 1: Freeze staging hiện tại

Đảm bảo staging hiện tại đang ổn:

```text
https://staging.c2-app-005.quangtm.site
```

Không deploy thêm thay đổi lớn vào staging trong lúc chuẩn bị release production, trừ hotfix cần thiết.

### Bước 2: Đồng bộ local branch

Trên máy local:

```bash
git fetch origin
git checkout dev
git pull origin dev
git checkout main
git pull origin main
```

### Bước 3: Tạo Pull Request `dev → main`

Trên GitHub:

```text
base: main
compare: dev
```

Việc cần kiểm tra trong PR:

- Conflict.
- Files thay đổi lớn.
- CI backend/frontend/docker.
- Các file `.env*` không chứa secret thật.
- Không commit nhầm backup/database/log.
- Public UI vẫn đúng.
- DevOps scripts không phá staging.

### Bước 4: Resolve conflict nếu có

Nếu GitHub báo conflict:

```bash
git checkout dev
git pull origin dev
git fetch origin main
git merge origin/main
```

Resolve conflict local, test:

```bash
cd FE
npm run build
```

Backend nếu cần:

```bash
python -m pytest tests -v
```

Sau đó:

```bash
git add .
git commit -m "chore: resolve dev into main release conflicts"
git push origin dev
```

Quay lại PR, đợi CI pass.

### Bước 5: Merge PR vào main

Chỉ merge khi:

- CI pass.
- Staging đã được kiểm tra.
- Không còn conflict.
- Team đồng ý đây là release candidate.

### Bước 6: Tạo tag release từ main

Sau khi merge:

```bash
git checkout main
git pull origin main
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions sẽ build image:

```text
c2-app-005-backend:v1.0.0
c2-app-005-frontend:v1.0.0
```

### Bước 7: Deploy production bằng tag v1.0.0

Set `.env.production`:

```env
BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:v1.0.0
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:v1.0.0
```

Deploy theo bước 13.

### Bước 8: Sau production

Sau khi production ổn:

```text
main = source of truth cho production v1.0.0
dev tiếp tục dùng cho phát triển tính năng mới
```

Nếu cần hotfix production:

```text
main → hotfix branch → PR main → tag patch → deploy production
main → merge/cherry-pick về dev
```

## 16. Rollback production

Nếu production lỗi, quay lại image tag cũ:

```env
BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:v0.9.0
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:v0.9.0
```

Redeploy:

```bash
docker compose --env-file .env.production \
  -p ocean-park-production \
  -f docker-compose.registry.yml \
  up -d
```

## 17. Checklist hoàn thành production

Production hoàn thành khi:

- DNS production resolve đúng VPS.
- Nginx production proxy đúng `3001/8001`.
- HTTPS production OK.
- Containers production chạy riêng với staging.
- Production DB volume riêng.
- Production dùng image tag cố định.
- Login/register hoạt động.
- Admin login được.
- Contact form lưu lead.
- Chat AI hoạt động.
- Browser không gọi `:8000` hoặc IP trực tiếp.
- Staging vẫn chạy bình thường.

## 18. Quyết định cần bạn duyệt

Trước khi thực hiện, cần xác nhận:

1. Production domain sẽ là:

```text
c2-app-005.quangtm.site
```

hay domain khác?

2. Có đồng ý dùng Nginx host cho production thay vì Caddy không?

3. Có đồng ý production chạy cùng VPS nhưng khác Docker project/port/database không?

4. Có đồng ý chuẩn hóa `dev → main` trước, rồi mới tag/deploy production không?

Đề xuất của tôi:

```text
Domain: c2-app-005.quangtm.site
Proxy: Nginx host
Deploy: cùng VPS, khác project/port/database
Release: PR dev → main, tag v1.0.0 từ main, deploy production từ tag đó
```
