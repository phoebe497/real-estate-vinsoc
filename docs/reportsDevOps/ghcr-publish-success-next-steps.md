# GHCR publish success and next steps

## Bối cảnh

Sau khi sửa workflow self-hosted runner labels và typo `seft-hosted`, GitHub Actions đã chạy thành công:

```text
Backend lint and tests: success
Frontend build: success
Docker build and publish: success
```

Trong GitHub Packages của organization đã xuất hiện 2 package:

```text
c2-app-005-backend
c2-app-005-frontend
```

Cả hai package đang ở trạng thái:

```text
Private
```

Đây là trạng thái đúng và an toàn cho staging/private project.

## Kết luận

CI/CD baseline đã đạt mục tiêu:

- Code được kiểm tra bằng Backend CI.
- Frontend build được kiểm tra.
- Docker images được build.
- Docker images được push lên GitHub Container Registry.
- VPS có thể pull image từ GHCR để deploy staging.

## Image name cần dùng

Với repo:

```text
AI20K-Build-Cohort-2/C2-App-005
```

Image staging dự kiến là:

```text
ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
```

Trong `.env` staging trên VPS cần set:

```env
BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
```

## Cách kiểm tra tags trong GitHub Packages

Trên GitHub:

1. Vào organization:

```text
AI20K-Build-Cohort-2
```

2. Chọn tab:

```text
Packages
```

3. Click package:

```text
c2-app-005-backend
```

4. Tìm mục:

```text
Versions
```

5. Kiểm tra version mới nhất có tag:

```text
dev
sha-xxxxxxx
```

6. Làm tương tự với:

```text
c2-app-005-frontend
```

## Vì package đang Private

VPS phải login GHCR trước khi pull image.

### Tạo GitHub token

User cần tự tạo token trên GitHub.

Nếu dùng classic token, cần quyền:

```text
read:packages
repo
```

Nếu dùng fine-grained token, cần quyền đọc repo/package tương ứng.

Không commit token vào repo.

### Login GHCR trên VPS

Trên VPS:

```bash
echo "<github-token>" | docker login ghcr.io -u <github-username> --password-stdin
```

Kết quả mong đợi:

```text
Login Succeeded
```

## Các bước tiếp theo trên VPS

## 1. Đi tới project folder

```bash
cd /opt/ocean-park-advisor
```

Nếu đã clone repo rồi:

```bash
git pull
```

Nếu muốn chắc chắn đang ở branch `dev`:

```bash
git checkout dev
git pull origin dev
```

## 2. Tạo file `.env`

```bash
cp .env.staging.example .env
nano .env
```

Điền tối thiểu:

```env
APP_ENV=staging
POSTGRES_DB=ocean_park_staging
POSTGRES_USER=ocean_staging
POSTGRES_PASSWORD=<strong-db-password>
DATABASE_URL=postgresql+psycopg://ocean_staging@database:5432/ocean_park_staging
AUTO_CREATE_TABLES=false
AUTO_SEED_CATALOG=true

JWT_SECRET_KEY=<random-secret-at-least-32-characters>
ADMIN_EMAIL=<your-admin-email>
ADMIN_PASSWORD=<strong-admin-password>
ADMIN_FULL_NAME=Staging Administrator

CORS_ORIGINS=http://<vps-ip>:3000
NEXT_PUBLIC_API_URL=http://<vps-ip>:8000/api/v1

PROJECT_NAME=ocean-park-staging
BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev

OPENAI_API_KEY=
LANGCHAIN_TRACING_V2=false
```

Nếu chưa có domain, dùng IP/port trước.

Nếu đã có domain HTTPS, dùng:

```env
CORS_ORIGINS=https://staging.your-domain.com
NEXT_PUBLIC_API_URL=https://api-staging.your-domain.com/api/v1
FRONTEND_DOMAIN=staging.your-domain.com
API_DOMAIN=api-staging.your-domain.com
ACME_EMAIL=<your-email>
```

## 3. Kiểm tra VPS prerequisites

```bash
bash scripts/deploy/check_vps_prerequisites.sh
```

Kết quả mong đợi:

```text
Prerequisites OK.
```

Nếu lỗi Docker permission, kiểm tra user đang chạy có quyền Docker không.

## 4. Pull thử image từ GHCR

```bash
docker pull ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
docker pull ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
```

Nếu pull thành công, nghĩa là:

- GHCR image tồn tại.
- VPS login GHCR đúng.
- Token có quyền đọc package.

## 5. Deploy staging bằng IP/port

Khi chưa setup domain/Cloudflare:

```bash
bash scripts/deploy/staging_deploy.sh
```

Script sẽ:

- kiểm tra `.env`
- validate compose config
- pull image
- start database/backend/frontend
- kiểm tra backend readiness
- kiểm tra frontend

## 6. Kiểm tra sau deploy

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml ps
curl http://localhost:8000/ready
curl -I http://localhost:3000
```

Kết quả backend mong đợi:

```json
{"status":"ready","database":"ok"}
```

Từ trình duyệt, test:

```text
http://<vps-ip>:3000
```

API:

```text
http://<vps-ip>:8000/ready
```

## 7. Nếu deploy staging bằng IP đã OK

Sau đó mới setup Cloudflare:

1. Tạo DNS record:

```text
staging.your-domain.com      -> VPS IP
api-staging.your-domain.com  -> VPS IP
```

2. Ban đầu để DNS Only.
3. Cập nhật `.env` sang HTTPS/domain.
4. Chạy:

```bash
bash scripts/deploy/staging_https_deploy.sh
```

5. Test:

```bash
curl https://api-staging.your-domain.com/ready
curl -I https://staging.your-domain.com
```

6. Sau khi HTTPS OK, bật Cloudflare Proxied và SSL/TLS Full strict.

## Checklist hiện tại

- [x] PR conflict đã xử lý.
- [x] Backend CI pass.
- [x] Frontend CI pass.
- [x] Docker build and publish pass.
- [x] GHCR có backend package.
- [x] GHCR có frontend package.
- [ ] Kiểm tra tag `dev` trong từng package.
- [ ] Login GHCR trên VPS.
- [ ] Tạo `.env` staging trên VPS.
- [ ] Pull thử image `:dev`.
- [ ] Deploy staging bằng IP/port.
- [ ] Setup Cloudflare/HTTPS sau khi staging bằng IP OK.

