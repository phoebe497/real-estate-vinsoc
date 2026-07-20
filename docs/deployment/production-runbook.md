# Production release, backup and rollback runbook

Runbook này dùng khi dự án đã có:

- GitHub Actions build/push image lên GHCR.
- VPS đã cài Docker.
- Domain/Cloudflare/HTTPS đã chuẩn bị.
- `.env` production đã được tạo trên VPS.

## Production release checklist

Trước khi deploy production:

- GitHub Actions pass trên commit/tag cần release.
- GHCR có backend/frontend image tag cần deploy.
- `.env` production không còn placeholder.
- `APP_ENV=production`.
- `AUTO_CREATE_TABLES=false`.
- `CORS_ORIGINS` chỉ chứa domain production.
- Cloudflare SSL/TLS mode là Full strict.
- VPS mở `80/443`, không mở public `3000/8000/5432`.
- Đã test staging trước.
- Đã có backup PostgreSQL mới nhất.

## Tạo release tag

Ví dụ:

```bash
git tag v0.8.0
git push origin v0.8.0
```

Sau đó kiểm tra GitHub Actions và GHCR.

## Production `.env`

Trên VPS:

```bash
cd /opt/ocean-park-advisor
cp .env.production.example .env
nano .env
```

Production nên dùng image tag version, không dùng `latest`:

```env
BACKEND_IMAGE=ghcr.io/<owner>/<repo>-backend:v0.8.0
FRONTEND_IMAGE=ghcr.io/<owner>/<repo>-frontend:v0.8.0
```

## Deploy production

```bash
bash scripts/deploy/production_deploy.sh
```

Script sẽ:

- kiểm tra Docker/Git/Curl
- kiểm tra `.env`
- bắt buộc `APP_ENV=production`
- chặn placeholder
- backup PostgreSQL trước deploy
- pull image từ GHCR
- chạy Docker Compose HTTPS
- kiểm tra backend `/ready`
- kiểm tra frontend HTTPS

Nếu đang deploy lần đầu và database chưa chạy nên chưa backup được, có thể tạm:

```bash
SKIP_BACKUP=true bash scripts/deploy/production_deploy.sh
```

Chỉ dùng `SKIP_BACKUP=true` khi chắc chắn không có dữ liệu cần giữ.

## Backup PostgreSQL thủ công

```bash
bash scripts/deploy/backup_postgres.sh
```

Backup được lưu vào:

```text
backups/postgres/
```

## Restore PostgreSQL

Restore là thao tác destructive. Cần xác nhận rõ:

```bash
RESTORE_CONFIRM=I_UNDERSTAND bash scripts/deploy/restore_postgres.sh backups/postgres/<backup-file>.dump
```

Sau restore:

```bash
docker compose --env-file .env -p ocean-park-production -f docker-compose.https.yml restart backend
curl https://api.example.com/ready
```

## Rollback image

Nếu release mới lỗi, rollback về image cũ:

```bash
bash scripts/deploy/rollback_images.sh \
  ghcr.io/<owner>/<repo>-backend:v0.7.0 \
  ghcr.io/<owner>/<repo>-frontend:v0.7.0
```

Script sẽ backup `.env`, thay `BACKEND_IMAGE`/`FRONTEND_IMAGE`, pull image cũ và chạy lại Compose.

## Kiểm tra sau deploy

```bash
docker compose --env-file .env -p ocean-park-production -f docker-compose.https.yml ps
curl https://api.example.com/ready
curl -I https://example.com
```

Kiểm tra logs:

```bash
docker compose --env-file .env -p ocean-park-production -f docker-compose.https.yml logs backend --tail 100
docker compose --env-file .env -p ocean-park-production -f docker-compose.https.yml logs frontend --tail 100
docker compose --env-file .env -p ocean-park-production -f docker-compose.https.yml logs caddy --tail 100
```

## Nguyên tắc production

- Không dùng `latest` cho production image.
- Không chạy `docker compose down -v` trên production nếu chưa backup.
- Không sửa `.env` trực tiếp mà không lưu lại version/backup.
- Luôn test staging trước production.
- Luôn có backup trước deploy có migration.
