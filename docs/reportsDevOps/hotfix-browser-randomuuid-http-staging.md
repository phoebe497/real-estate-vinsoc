# Hotfix: frontend crash on HTTP staging because crypto.randomUUID is unavailable

## Bối cảnh

Sau khi staging deploy thành công, khi mở bằng IP VPS trên trình duyệt:

```text
http://<vps-ip>:3000
```

Giao diện hiện:

```text
This page couldn't load
```

Console browser báo:

```text
Uncaught TypeError: crypto.randomUUID is not a function
```

## Nguyên nhân

Frontend `ChatWidget` tạo `sessionId` bằng:

```ts
crypto.randomUUID()
```

API này không phải lúc nào cũng khả dụng khi chạy trên HTTP/IP public. Nhiều browser chỉ hỗ trợ đầy đủ Web Crypto APIs trong secure context:

- `https://...`
- hoặc `localhost`

Vì staging hiện đang mở bằng:

```text
http://<vps-ip>:3000
```

nên `crypto.randomUUID` có thể không tồn tại, làm React component crash ngay lúc load trang.

## Phương án đã áp dụng

Loại bỏ hoàn toàn việc gọi `crypto.randomUUID()` trong:

```text
FE/src/components/chat-widget.tsx
```

Lý do:

- `session_id` của chat chỉ dùng để gom tin nhắn trong cùng một phiên.
- Đây không phải secret/token bảo mật.
- Không cần phụ thuộc Web Crypto API.
- Staging HTTP/IP cần chạy ổn trên nhiều browser hơn.

Logic mới dùng timestamp và random string:

```ts
function createSessionId() {
  return `session-${Date.now().toString(36)}-${Math.random()
    .toString(36)
    .slice(2, 10)}`;
}
```

Sau đó:

```ts
const [sessionId] = useState(createSessionId);
```

## Kết quả mong đợi

Frontend không còn crash khi chạy trên:

```text
http://<vps-ip>:3000
```

Sau này khi chuyển sang HTTPS qua Cloudflare/domain, có thể cân nhắc dùng lại `crypto.randomUUID`, nhưng hiện tại không cần thiết cho mục tiêu staging.

## Cách test local

Build frontend:

```bash
cd FE
npm run build
```

## Cách deploy lại staging

Commit và push code lên nhánh `dev`:

```bash
git add FE/src/components/chat-widget.tsx docs/reportsDevOps/hotfix-browser-randomuuid-http-staging.md docs/reportsDevOps/README.md
git commit -m "fix: remove crypto dependency from chat session id"
git push origin dev
```

Chờ GitHub Actions build/publish frontend image mới.

Trên VPS:

```bash
cd /opt/ocean-park-advisor
git pull origin dev
bash scripts/deploy/staging_deploy.sh
```

Sau đó mở lại:

```text
http://<vps-ip>:3000
```

Nếu trình duyệt vẫn giữ cache bundle cũ, hard refresh:

```text
Ctrl + F5
```

## Nếu vẫn thấy lỗi randomUUID sau khi đã sửa code

Nếu console vẫn báo file JS cũ, ví dụ:

```text
288io5wu1m3gv.js
Uncaught TypeError: crypto.randomUUID is not a function
```

trong khi local build mới đã tạo chunk khác, nghĩa là staging/browser vẫn đang dùng frontend bundle cũ.

Các nguyên nhân thường gặp:

- Chưa commit/push code fix lên `dev`.
- GitHub Actions chưa build/publish frontend image mới.
- VPS chưa pull image mới từ GHCR.
- Container frontend chưa được recreate.
- Browser cache vẫn giữ JS bundle cũ.

Kiểm tra trên VPS:

```bash
cd /opt/ocean-park-advisor
git pull origin dev
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml pull frontend
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml up -d --force-recreate frontend
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs frontend --tail 80
```

Sau đó hard refresh:

```text
Ctrl + F5
```

hoặc mở bằng tab ẩn danh.

Nếu cần kiểm tra chắc chắn container đang serve bundle nào:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml exec frontend sh -lc 'find /app/.next/static/chunks -type f | head -20'
```

Nếu vẫn thấy chunk cũ trên browser nhưng container đã có chunk mới, nguyên nhân là browser/proxy cache.
