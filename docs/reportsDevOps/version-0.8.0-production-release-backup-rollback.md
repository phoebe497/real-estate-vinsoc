# DevOps v0.8.0 - Production release, backup and rollback

## Mục tiêu

Hoàn thiện lớp an toàn trước production:

- Có production release checklist.
- Có script deploy production.
- Có backup PostgreSQL trước deploy.
- Có restore PostgreSQL khi cần.
- Có rollback image khi release lỗi.
- Có runbook để thao tác production theo quy trình.

Version này vẫn chưa tự thao tác lên VPS thật. Đây là bộ công cụ và tài liệu để khi bạn có VPS/domain/GHCR thật thì deploy có kiểm soát.

## Công việc đã làm

### 1. Thêm production runbook

File mới:

```text
docs/deployment/production-runbook.md
```

Runbook gồm:

- checklist trước production
- tạo release tag
- chuẩn bị `.env`
- deploy production
- backup
- restore
- rollback image
- kiểm tra sau deploy
- nguyên tắc production

### 2. Thêm script backup PostgreSQL

File mới:

```text
scripts/deploy/backup_postgres.sh
```

Script tạo backup dạng custom dump:

```bash
pg_dump --format=custom --no-owner --no-acl
```

Backup được lưu vào:

```text
backups/postgres/
```

Thư mục `backups/` đã được thêm vào `.gitignore` để không commit nhầm dữ liệu backup.

### 3. Thêm script restore PostgreSQL

File mới:

```text
scripts/deploy/restore_postgres.sh
```

Restore là thao tác destructive nên script bắt buộc xác nhận:

```bash
RESTORE_CONFIRM=I_UNDERSTAND
```

Cách chạy:

```bash
RESTORE_CONFIRM=I_UNDERSTAND bash scripts/deploy/restore_postgres.sh backups/postgres/<backup-file>.dump
```

### 4. Thêm script deploy production

File mới:

```text
scripts/deploy/production_deploy.sh
```

Script thực hiện:

- kiểm tra VPS prerequisites
- kiểm tra `.env`
- bắt buộc `APP_ENV=production`
- chặn placeholder
- validate compose HTTPS config
- backup PostgreSQL trước deploy
- pull image từ GHCR
- chạy production services
- kiểm tra backend `/ready`
- kiểm tra frontend HTTPS

Lệnh chạy:

```bash
bash scripts/deploy/production_deploy.sh
```

Nếu deploy lần đầu chưa có dữ liệu/database đang chạy, có thể bỏ backup:

```bash
SKIP_BACKUP=true bash scripts/deploy/production_deploy.sh
```

Chỉ dùng `SKIP_BACKUP=true` khi chắc chắn không có data cần giữ.

### 5. Thêm script rollback image

File mới:

```text
scripts/deploy/rollback_images.sh
```

Cách dùng:

```bash
bash scripts/deploy/rollback_images.sh \
  ghcr.io/<owner>/<repo>-backend:v0.7.0 \
  ghcr.io/<owner>/<repo>-frontend:v0.7.0
```

Script sẽ:

- backup file `.env` hiện tại
- thay `BACKEND_IMAGE`
- thay `FRONTEND_IMAGE`
- pull image cũ
- chạy lại Compose

### 6. Cập nhật production env template

Cập nhật:

```text
.env.production.example
```

Production image tag chuyển sang:

```env
BACKEND_IMAGE=ghcr.io/your-github-user-or-org/your-repo-backend:v0.8.0
FRONTEND_IMAGE=ghcr.io/your-github-user-or-org/your-repo-frontend:v0.8.0
```

### 7. Bump version

Cập nhật version:

- backend/project: `0.8.0`
- frontend package: `0.8.0`
- frontend lockfile: `0.8.0`

## Phương án áp dụng

Mình chọn hướng production đơn giản nhưng đủ an toàn:

```text
Release tag -> GHCR image tag -> VPS pulls exact tag -> backup DB -> deploy -> health check
```

Nguyên tắc quan trọng:

- Production không dùng `latest`.
- Production deploy bằng tag cụ thể như `v0.8.0`.
- Trước deploy production có backup DB.
- Rollback bằng cách quay lại image tag cũ.
- Không xoá volume production nếu chưa backup.

## Cách sử dụng trên VPS production

### 1. Tạo release tag

Trên máy dev:

```bash
git tag v0.8.0
git push origin v0.8.0
```

Đợi GitHub Actions build/push image lên GHCR.

### 2. Chuẩn bị production VPS

```bash
ssh user@your-vps-ip
cd /opt/ocean-park-advisor
git pull
cp .env.production.example .env
nano .env
```

Đảm bảo `.env` dùng domain/image thật, không còn placeholder.

### 3. Deploy production

```bash
bash scripts/deploy/production_deploy.sh
```

### 4. Kiểm tra sau deploy

```bash
docker compose --env-file .env -p ocean-park-production -f docker-compose.https.yml ps
curl https://api.example.com/ready
curl -I https://example.com
```

Kết quả backend mong đợi:

```json
{"status":"ready","database":"ok"}
```

## Backup thủ công

```bash
bash scripts/deploy/backup_postgres.sh
```

## Restore

```bash
RESTORE_CONFIRM=I_UNDERSTAND bash scripts/deploy/restore_postgres.sh backups/postgres/<backup-file>.dump
```

## Rollback

```bash
bash scripts/deploy/rollback_images.sh \
  ghcr.io/<owner>/<repo>-backend:v0.7.0 \
  ghcr.io/<owner>/<repo>-frontend:v0.7.0
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

Compose HTTPS production:

```powershell
docker compose --env-file .env.production.example -f docker-compose.https.yml config --quiet
```

Kết quả: hợp lệ.

## Lưu ý

- Máy Windows local chưa có WSL distro nên chưa chạy được `bash -n` trực tiếp tại local.
- Khi lên VPS Linux, nên kiểm tra:

```bash
bash -n scripts/deploy/backup_postgres.sh
bash -n scripts/deploy/restore_postgres.sh
bash -n scripts/deploy/production_deploy.sh
bash -n scripts/deploy/rollback_images.sh
```

- Backup cần được copy ra ngoài VPS định kỳ trong production thật, ví dụ object storage hoặc máy backup riêng.

## Trạng thái sau v0.8.0

Roadmap DevOps ban đầu đã hoàn tất ở mức baseline:

- v0.3.1 Security/environment baseline
- v0.4.0 Production Docker baseline
- v0.5.0 CI/container registry
- v0.6.0 VPS staging deployment
- v0.7.0 Cloudflare/HTTPS/reverse proxy
- v0.8.0 Production release/backup/rollback


