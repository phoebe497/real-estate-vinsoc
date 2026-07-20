# Báo cáo tiến độ domain staging + Nginx reverse proxy

Ngày: 2026-06-28  
Domain: `staging.c2-app-005.quangtm.site`  
VPS: `103.149.87.83`

## 1. Trạng thái đã xác nhận

DNS đã resolve đúng:

```text
staging.c2-app-005.quangtm.site -> 103.149.87.83
```

Nginx trên VPS đã hoạt động:

```text
nginx/1.18.0 (Ubuntu)
```

HTTP qua domain đã vào frontend thành công:

```bash
curl -I http://staging.c2-app-005.quangtm.site
```

Kết quả:

```text
HTTP/1.1 200 OK
X-Powered-By: Next.js
```

Backend docs cũng đi qua domain thành công:

```bash
curl http://staging.c2-app-005.quangtm.site/docs
```

Kết quả: trả về Swagger UI.

## 2. Phân tích script deploy

File:

```text
scripts/deploy/staging_deploy.sh
```

Script mặc định dùng:

```bash
PROJECT_NAME="${PROJECT_NAME:-ocean-park-staging}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.registry.yml}"
ENV_FILE="${ENV_FILE:-.env}"
BACKEND_READY_URL="${BACKEND_READY_URL:-http://localhost:8000/ready}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
```

Kết luận:

- Staging deploy hiện đọc `.env` ở root project.
- Backend readiness thật là `/ready`, không phải `/api/v1/ready`.
- Frontend readiness check vẫn dùng local `localhost:3000`, phù hợp vì script chạy trực tiếp trên VPS.

## 3. Phân tích compose registry

File:

```text
docker-compose.registry.yml
```

Frontend service hiện có:

```yaml
frontend:
  image: ${FRONTEND_IMAGE}
  environment:
    API_URL_INTERNAL: http://backend:8000/api/v1
```

Kết luận quan trọng:

- `API_URL_INTERNAL` chỉ phục vụ server-side fetch trong Next.js.
- `NEXT_PUBLIC_API_URL` của browser thường được đóng gói lúc build Docker image.
- Nếu image build với `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`, frontend có nguy cơ gọi sai khi chạy trên domain.

## 4. Fix đã thực hiện trong source

File đã sửa:

```text
FE/src/lib/api.ts
```

Trước đó, khi browser chạy trên domain thật nhưng config vẫn là localhost, code tự đổi thành:

```text
http://<domain>:8000/api/v1
```

Điều này không đúng với kiến trúc reverse proxy vì ta muốn API đi qua cùng domain:

```text
http://staging.c2-app-005.quangtm.site/api/v1
```

Đã sửa resolver thành:

```ts
return `${window.location.origin}/api/v1`;
```

Kết quả:

- Nếu build image lỡ dùng localhost, khi chạy trên domain thật frontend vẫn tự gọi cùng origin.
- Không cần public port `8000` cho browser.
- Phù hợp với Nginx reverse proxy:

```text
/api/v1 -> backend:8000/api/v1
/agent  -> backend:8000/agent
```

## 5. Test đã chạy

Local frontend build:

```bash
cd FE
npm run build
```

Kết quả:

```text
Compiled successfully
TypeScript OK
Static pages generated successfully
```

## 6. Bước tiếp theo trên VPS

### 6.1. Cập nhật `.env`

Vì staging script dùng `.env`, cần backup trước:

```bash
cp .env .env.backup-before-domain
```

Sau đó kiểm tra/sửa:

```env
NEXT_PUBLIC_API_URL=http://staging.c2-app-005.quangtm.site/api/v1
CORS_ORIGINS=http://staging.c2-app-005.quangtm.site,http://103.149.87.83:3000,http://localhost:3000,http://127.0.0.1:3000
```

Sau khi có HTTPS sẽ đổi thành:

```env
NEXT_PUBLIC_API_URL=https://staging.c2-app-005.quangtm.site/api/v1
CORS_ORIGINS=https://staging.c2-app-005.quangtm.site
```

### 6.2. Commit/push source fix

Cần commit file:

```text
FE/src/lib/api.ts
```

Sau khi GitHub Actions build/publish image mới, VPS redeploy:

```bash
bash scripts/deploy/staging_deploy.sh
```

### 6.3. Test domain

Test frontend:

```bash
curl -I http://staging.c2-app-005.quangtm.site
```

Test backend:

```bash
curl http://staging.c2-app-005.quangtm.site/docs
curl http://staging.c2-app-005.quangtm.site/openapi.json
```

Trong browser DevTools:

- Không được còn request tới `localhost:8000`.
- API phải đi qua `/api/v1`.
- Chat phải đi qua `/agent/chat`.

## 7. Sau khi HTTP ổn

Cấp HTTPS bằng Certbot:

```bash
sudo certbot --nginx -d staging.c2-app-005.quangtm.site
```

Sau HTTPS, cập nhật `.env` sang HTTPS và redeploy lại.

