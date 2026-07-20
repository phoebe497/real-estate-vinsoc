# Manual platform actions checklist

## Mục tiêu

Tài liệu này tổng hợp các bước user phải tự thực hiện trên các nền tảng bên ngoài mà Codex không thể thao tác thay trực tiếp:

- GitHub
- GitHub Actions
- GHCR
- VPS
- Cloudflare
- Domain/DNS

Các bước trong repo đã được chuẩn bị sẵn bằng code, Docker Compose, scripts và reports. Phần còn lại là thao tác trên tài khoản/nền tảng thật của bạn.

## Trạng thái hiện tại

Bạn đã:

- Push code lên branch `TranMinhQuang`.
- Tạo Pull Request vào branch `dev`.
- Resolve conflict.
- Backend CI và Frontend CI đã chạy được sau khi đổi sang `self-hosted`.
- Repo đã clone được lên VPS tại:

```text
/opt/ocean-park-advisor
```

Docker build and publish trên PR bị skip là bình thường vì workflow đang có:

```yaml
if: github.event_name != 'pull_request'
```

Docker image chỉ build/push sau khi merge vào `dev` hoặc push tag release.

## Việc cần làm tiếp theo

## 1. GitHub Pull Request

### Mục tiêu

Merge branch:

```text
TranMinhQuang -> dev
```

### Việc user cần làm

Trên GitHub:

1. Mở Pull Request hiện tại.
2. Kiểm tra:
   - No conflicts with base branch.
   - Backend CI pass.
   - Frontend CI pass.
   - Docker job skipped trên PR là bình thường.
3. Nếu team đồng ý, bấm:

```text
Merge pull request
```

### Kết quả mong đợi

Sau khi merge, branch `dev` nhận toàn bộ code DevOps + AI feature.

## 2. GitHub Actions sau khi merge vào dev

### Mục tiêu

Workflow chạy trên event:

```text
push vào dev
```

Lúc này Docker job không còn bị skip nữa.

### Việc user cần làm

Vào:

```text
GitHub repo -> Actions
```

Mở workflow mới nhất sau merge vào `dev`.

Kiểm tra 3 job:

```text
Backend lint and tests
Frontend build
Docker build and publish
```

### Kết quả mong đợi

```text
Backend lint and tests: success
Frontend build: success
Docker build and publish: success
```

Nếu Docker job vẫn bị billing block:

- Cần xử lý Billing & plans của GitHub account/organization.
- Hoặc cân nhắc đổi Docker job sang `self-hosted` nếu runner có Docker/Buildx ổn định.

## 3. GHCR packages

### Mục tiêu

Sau khi Docker build and publish pass, GHCR phải có image:

```text
ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
```

Tên image có thể khác nếu GitHub repository owner/name khác. Workflow dùng pattern:

```text
ghcr.io/<owner>/<repo>-backend:<tag>
ghcr.io/<owner>/<repo>-frontend:<tag>
```

### Việc user cần làm

Vào:

```text
GitHub repo -> Packages
```

Kiểm tra có 2 package:

```text
c2-app-005-backend
c2-app-005-frontend
```

và tag:

```text
dev
sha-xxxxxxx
```

### Nếu package private

VPS cần login GHCR.

Trên GitHub, tạo token có quyền đọc package/repo.

Trên VPS chạy:

```bash
echo "<github-token>" | docker login ghcr.io -u <github-username> --password-stdin
```

Không ghi token vào repo.

## 4. VPS preparation

### Mục tiêu

VPS đủ điều kiện chạy Docker Compose deploy.

### Việc user cần làm trên VPS

SSH vào VPS:

```bash
ssh root@your-vps-ip
```

Đi tới folder project:

```bash
cd /opt/ocean-park-advisor
```

Kiểm tra công cụ:

```bash
docker version
docker compose version
git --version
curl --version
```

Hoặc dùng script:

```bash
bash scripts/deploy/check_vps_prerequisites.sh
```

### Kết quả mong đợi

Script báo:

```text
Prerequisites OK.
```

Nếu thiếu Docker, cài Docker Engine và Docker Compose plugin theo Docker docs chính thức.

## 5. Tạo file .env staging trên VPS

### Mục tiêu

Tạo file `.env` thật trên VPS. File này không commit lên Git.

### Việc user cần làm

Trên VPS:

```bash
cd /opt/ocean-park-advisor
cp .env.staging.example .env
nano .env
```

Điền các biến quan trọng:

```env
APP_ENV=staging
POSTGRES_DB=ocean_park_staging
POSTGRES_USER=ocean_staging
POSTGRES_PASSWORD=<strong-db-password>
JWT_SECRET_KEY=<random-secret-at-least-32-characters>
ADMIN_EMAIL=<your-admin-email>
ADMIN_PASSWORD=<strong-admin-password>
CORS_ORIGINS=http://<vps-ip>:3000
NEXT_PUBLIC_API_URL=http://<vps-ip>:8000/api/v1
PROJECT_NAME=ocean-park-staging
BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
```

Nếu đã có domain HTTPS:

```env
CORS_ORIGINS=https://staging.your-domain.com
NEXT_PUBLIC_API_URL=https://api-staging.your-domain.com/api/v1
FRONTEND_DOMAIN=staging.your-domain.com
API_DOMAIN=api-staging.your-domain.com
ACME_EMAIL=<your-email>
```

### Lưu ý

Không để placeholder:

```text
replace-with
your-repo
example.com
```

Script deploy sẽ chặn nếu còn placeholder.

## 6. Deploy staging không HTTPS

### Khi nào dùng

Dùng khi bạn chưa setup domain/Cloudflare.

### Việc user cần làm

Trên VPS:

```bash
cd /opt/ocean-park-advisor
bash scripts/deploy/staging_deploy.sh
```

### Kết quả mong đợi

```text
Staging deployment completed successfully.
```

Kiểm tra:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml ps
curl http://localhost:8000/ready
curl -I http://localhost:3000
```

Backend mong đợi:

```json
{"status":"ready","database":"ok"}
```

## 7. Cloudflare/DNS setup

### Khi nào làm

Làm sau khi:

- Docker image `:dev` đã có trên GHCR.
- VPS chạy staging OK bằng IP/port hoặc bạn đã sẵn sàng dùng domain.

### Việc user cần làm trên Cloudflare

Tạo DNS records:

| Type | Name | Target |
| --- | --- | --- |
| A | staging | VPS public IP |
| A | api-staging | VPS public IP |

Ban đầu nên để:

```text
DNS Only
```

Sau khi HTTPS chạy ổn, có thể bật:

```text
Proxied
```

SSL/TLS mode nên đặt:

```text
Full strict
```

## 8. Deploy staging với HTTPS

### Khi nào dùng

Dùng khi đã có domain và DNS trỏ về VPS.

### Việc user cần làm

Trên VPS cập nhật `.env`:

```env
CORS_ORIGINS=https://staging.your-domain.com
NEXT_PUBLIC_API_URL=https://api-staging.your-domain.com/api/v1
FRONTEND_DOMAIN=staging.your-domain.com
API_DOMAIN=api-staging.your-domain.com
ACME_EMAIL=<your-email>
```

Chạy:

```bash
bash scripts/deploy/staging_https_deploy.sh
```

Kiểm tra:

```bash
curl https://api-staging.your-domain.com/ready
curl -I https://staging.your-domain.com
```

## 9. Sau khi staging OK

### Mục tiêu

Chuẩn bị production sau này.

### Việc user cần làm

Chưa cần deploy production ngay.

Khi staging đã ổn, mới tạo release tag:

```bash
git tag v0.8.0
git push origin v0.8.0
```

Sau đó kiểm tra GHCR có image tag:

```text
v0.8.0
```

Production dùng:

```text
.env.production.example
docker-compose.https.yml
scripts/deploy/production_deploy.sh
```

## Checklist tổng hợp

### GitHub

- [ ] Merge PR `TranMinhQuang -> dev`
- [ ] Actions sau merge vào `dev` chạy
- [ ] Backend CI pass
- [ ] Frontend CI pass
- [ ] Docker build and publish pass

### GHCR

- [ ] Có backend image tag `dev`
- [ ] Có frontend image tag `dev`
- [ ] Nếu package private, VPS login được GHCR

### VPS

- [ ] Repo đã clone tại `/opt/ocean-park-advisor`
- [ ] Docker chạy được
- [ ] Docker Compose chạy được
- [ ] `.env` staging đã tạo
- [ ] Không còn placeholder trong `.env`
- [ ] `staging_deploy.sh` chạy thành công

### Cloudflare

- [ ] DNS record staging trỏ về VPS
- [ ] DNS record api-staging trỏ về VPS
- [ ] Ban đầu DNS Only
- [ ] HTTPS deploy thành công
- [ ] SSL/TLS mode Full strict
- [ ] Có thể bật Proxied sau khi HTTPS OK

## Thứ tự khuyến nghị từ lúc này

1. Merge PR vào `dev`.
2. Đợi Actions chạy sau merge.
3. Kiểm tra Docker build and publish.
4. Kiểm tra GHCR image tag `dev`.
5. Tạo `.env` trên VPS.
6. Login GHCR trên VPS nếu package private.
7. Deploy staging bằng IP/port trước.
8. Nếu OK, setup Cloudflare DNS.
9. Deploy staging HTTPS.
10. Demo cho mentor.

