# Cloudflare and HTTPS deployment guide

Tài liệu này dùng cho staging/production khi bạn đã có VPS, domain và GHCR images.

## Mục tiêu

- Public traffic đi vào Cloudflare.
- Cloudflare trỏ về VPS.
- Caddy trên VPS nhận request ở port `80/443`.
- Caddy reverse proxy:
  - frontend domain -> `frontend:3000`
  - API domain -> `backend:8000`
- Backend/frontend không expose port trực tiếp ra internet.

## Kiến trúc

```text
Browser
  |
Cloudflare DNS / Proxy
  |
VPS public IP :80/:443
  |
Caddy container
  |------ frontend:3000
  |
  └------ backend:8000
```

## Domain đề xuất

Staging:

```text
staging.example.com      -> frontend
api-staging.example.com  -> backend API
```

Production:

```text
example.com      -> frontend
api.example.com  -> backend API
```

## Cloudflare DNS

Tạo các record:

| Type | Name | Target |
| --- | --- | --- |
| A | staging | VPS public IP |
| A | api-staging | VPS public IP |

Ban đầu nên để DNS Only để Caddy lấy chứng chỉ TLS dễ nhất. Sau khi HTTPS hoạt động, có thể bật Proxied.

## Cloudflare SSL/TLS mode

Nên dùng:

```text
Full (strict)
```

Lý do: Cloudflare sẽ kiểm tra origin server có certificate hợp lệ. Với Caddy, certificate được cấp tự động bởi Let's Encrypt/ZeroSSL khi DNS trỏ đúng và port `80/443` mở.

Không nên dùng lâu dài:

```text
Flexible
```

Vì Flexible chỉ mã hoá từ browser tới Cloudflare, còn Cloudflare tới VPS có thể không mã hoá.

## Firewall VPS

Mở:

```text
22/tcp   SSH
80/tcp   HTTP challenge and redirect
443/tcp  HTTPS
443/udp  HTTP/3 optional
```

Không cần mở public:

```text
8000 backend
3000 frontend
5432 database
```

Khi dùng `docker-compose.https.yml`, chỉ Caddy publish `80/443`.

## Chuẩn bị `.env`

Ví dụ staging:

```env
APP_ENV=staging
CORS_ORIGINS=https://staging.your-domain.com
NEXT_PUBLIC_API_URL=https://api-staging.your-domain.com/api/v1
FRONTEND_DOMAIN=staging.your-domain.com
API_DOMAIN=api-staging.your-domain.com
ACME_EMAIL=admin@your-domain.com
BACKEND_IMAGE=ghcr.io/<owner>/<repo>-backend:dev
FRONTEND_IMAGE=ghcr.io/<owner>/<repo>-frontend:dev
```

## Deploy HTTPS staging

Trên VPS:

```bash
cd /opt/ocean-park-advisor
git pull
bash scripts/deploy/staging_https_deploy.sh
```

Script dùng:

```text
docker-compose.https.yml
deploy/caddy/Caddyfile
```

## Kiểm tra

Backend:

```bash
curl https://api-staging.your-domain.com/ready
```

Kết quả:

```json
{"status":"ready","database":"ok"}
```

Frontend:

```bash
curl -I https://staging.your-domain.com
```

Kết quả mong đợi: HTTP `200` hoặc `308/301` redirect sang HTTPS nếu gọi từ HTTP.

Container:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.https.yml ps
```

Logs Caddy:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.https.yml logs caddy --tail 120
```

## Quy trình khuyến nghị

1. Tạo DNS record trên Cloudflare ở trạng thái DNS Only.
2. SSH vào VPS.
3. Đảm bảo firewall mở `80/443`.
4. Chạy `bash scripts/deploy/staging_https_deploy.sh`.
5. Test HTTPS domain.
6. Sau khi HTTPS ổn, bật Cloudflare Proxied nếu muốn dùng CDN/WAF.
7. Đặt SSL/TLS mode là Full strict.

## Rollback nhanh

Nếu HTTPS proxy lỗi nhưng muốn quay lại test bằng port:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.https.yml down
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml up -d
```

Lưu ý: không dùng `down -v` nếu muốn giữ database volume.
