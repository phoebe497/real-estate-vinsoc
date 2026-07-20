# Version 0.9.0 - Kế hoạch tự động hóa deploy staging từ GitHub Actions lên VPS

Ngày lập kế hoạch: 2026-06-29  
Trạng thái: Chờ duyệt trước khi thực hiện  
Mục tiêu: Nâng cấp từ `CI + manual staging deployment` lên `CI + automated staging CD`

## 1. Hiện trạng hiện tại

Quy trình hiện tại:

```text
Code local
  ↓
Push lên branch TranMinhQuang
  ↓
Tạo Pull Request vào dev
  ↓
Merge vào dev
  ↓
GitHub Actions chạy:
  ├── Backend lint/tests
  ├── Frontend build
  └── Docker build & publish image lên GHCR
  ↓
User SSH vào VPS thủ công
  ↓
git pull code từ dev
  ↓
bash scripts/deploy/staging_deploy.sh
```

Đánh giá:

```text
CI: Có
Docker image publish: Có
CD: Có script nhưng deploy thủ công
Full CI/CD: Chưa
```

Tên đúng hiện tại:

```text
CI + Manual CD
```

## 2. Mục tiêu version 0.9.0

Sau khi hoàn thành, quy trình mong muốn:

```text
Code local
  ↓
Push TranMinhQuang
  ↓
PR vào dev
  ↓
Merge dev
  ↓
GitHub Actions chạy test/build
  ↓
Docker image được publish lên GHCR
  ↓
GitHub Actions tự SSH vào VPS
  ↓
VPS pull code dev mới nhất
  ↓
VPS pull image dev mới nhất
  ↓
Chạy scripts/deploy/staging_deploy.sh
  ↓
Healthcheck domain staging
  ↓
Báo deploy success/fail trên GitHub Actions
```

Domain staging:

```text
https://staging.c2-app-005.quangtm.site
```

## 3. Phạm vi thực hiện

### Sẽ làm

- Thiết kế job deploy staging trong GitHub Actions.
- Chuẩn hóa biến/secrets cần thiết.
- Thêm job `deploy-staging` sau job Docker build & publish.
- Job chỉ chạy khi push vào `dev`.
- Không chạy deploy khi pull request.
- SSH vào VPS và chạy script deploy staging hiện có.
- Thêm healthcheck sau deploy.
- Viết report hướng dẫn setup secrets và cách test.

### Không làm trong version này

- Không tự động deploy production.
- Không thay đổi database schema.
- Không đổi domain.
- Không đổi kiến trúc Nginx hiện tại.
- Không expose database.
- Không thay đổi logic app/AI/Admin.

## 4. Kiến trúc CD đề xuất

```text
GitHub Actions
  ↓ SSH private key
VPS root/deploy user
  ↓
/opt/ocean-park-advisor
  ↓
git fetch/pull dev
  ↓
docker compose pull
  ↓
docker compose up -d
  ↓
Nginx reverse proxy
  ↓
https://staging.c2-app-005.quangtm.site
```

## 5. Secrets và variables cần chuẩn bị

### GitHub Secrets

Cần tạo trong:

```text
GitHub Repo → Settings → Secrets and variables → Actions → Secrets
```

Đề xuất:

```text
STAGING_SSH_PRIVATE_KEY
```

Nội dung là private key dùng riêng cho GitHub Actions SSH vào VPS.

Không nên dùng SSH key cá nhân chính nếu có thể tránh.

### GitHub Variables

Cần tạo trong:

```text
GitHub Repo → Settings → Secrets and variables → Actions → Variables
```

Đề xuất:

```text
STAGING_HOST=103.149.87.83
STAGING_USER=root
STAGING_APP_DIR=/opt/ocean-park-advisor
STAGING_DOMAIN=https://staging.c2-app-005.quangtm.site
NEXT_PUBLIC_API_URL=https://staging.c2-app-005.quangtm.site/api/v1
```

Nếu sau này tạo user riêng `deploy`, đổi:

```text
STAGING_USER=deploy
```

## 6. SSH key deploy đề xuất

### Tạo SSH key riêng trên máy local hoặc VPS

Ví dụ trên máy local:

```bash
ssh-keygen -t ed25519 -C "github-actions-staging-c2-app-005" -f ~/.ssh/c2_app_005_staging_deploy
```

Sẽ có:

```text
~/.ssh/c2_app_005_staging_deploy
~/.ssh/c2_app_005_staging_deploy.pub
```

### Add public key vào VPS

Trên VPS:

```bash
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
```

Dán nội dung file:

```text
c2_app_005_staging_deploy.pub
```

Set permission:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Add private key vào GitHub Secret

Secret:

```text
STAGING_SSH_PRIVATE_KEY
```

Value:

```text
nội dung file ~/.ssh/c2_app_005_staging_deploy
```

## 7. Workflow GitHub Actions đề xuất

Thêm job sau `docker-images`:

```yaml
deploy-staging:
  name: Deploy staging to VPS
  runs-on: [self-hosted, Linux, X64, cohort2]
  needs: [docker-images]
  if: github.event_name == 'push' && github.ref == 'refs/heads/dev'

  steps:
    - name: Deploy over SSH
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ vars.STAGING_HOST }}
        username: ${{ vars.STAGING_USER }}
        key: ${{ secrets.STAGING_SSH_PRIVATE_KEY }}
        script_stop: true
        script: |
          cd "${{ vars.STAGING_APP_DIR }}"
          git fetch origin dev
          git checkout dev
          git pull --ff-only origin dev
          bash scripts/deploy/staging_deploy.sh

    - name: Check staging frontend
      run: curl -fsS "${{ vars.STAGING_DOMAIN }}" >/dev/null

    - name: Check staging API docs
      run: curl -fsS "${{ vars.STAGING_DOMAIN }}/openapi.json" >/dev/null
```

Ghi chú:

- Job này chỉ chạy sau khi `docker-images` pass.
- Không chạy trên pull request.
- Chỉ chạy khi code đã merge/push vào `dev`.

## 8. Điều kiện để job deploy hoạt động đúng

VPS cần có sẵn:

- Git repo ở:

```text
/opt/ocean-park-advisor
```

- Branch `dev` tracking đúng remote.
- File `.env` staging đúng.
- Docker login GHCR nếu image private.
- Docker Compose hoạt động.
- Nginx/HTTPS đã cấu hình.

Kiểm tra Docker login GHCR trên VPS:

```bash
docker pull ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
docker pull ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
```

Nếu pull được thì deploy script sẽ pull được.

## 9. Rủi ro và cách xử lý

### Rủi ro 1: GitHub Actions SSH không vào được VPS

Dấu hiệu:

```text
Permission denied (publickey)
```

Xử lý:

- Kiểm tra public key đã nằm trong `~/.ssh/authorized_keys` trên VPS.
- Kiểm tra private key trong GitHub Secret đúng format.
- Kiểm tra user `root` hoặc `deploy`.

### Rủi ro 2: VPS không pull được GHCR image

Dấu hiệu:

```text
denied: permission denied
```

Xử lý:

- `docker login ghcr.io` trên VPS.
- Dùng GitHub PAT có quyền `read:packages`.
- Hoặc set package visibility phù hợp.

### Rủi ro 3: `git pull --ff-only` fail

Dấu hiệu:

```text
Not possible to fast-forward
```

Nguyên nhân:

- VPS có local changes.
- Branch lệch remote.

Xử lý:

- Kiểm tra:

```bash
git status
```

- Không dùng `reset --hard` tự động ở version đầu để tránh mất thay đổi ngoài ý muốn.

### Rủi ro 4: Deploy xong nhưng app lỗi

Xử lý:

- Xem logs:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs backend --tail 100
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs frontend --tail 100
```

- Rollback bằng image tag trước nếu cần.

## 10. Checklist test sau khi hoàn thành

Sau khi merge vào `dev`, kiểm tra:

1. GitHub Actions chạy:

```text
Backend lint and tests
Frontend build
Docker build and publish
Deploy staging to VPS
```

2. GitHub Actions báo success.

3. VPS containers healthy:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml ps
```

4. Domain mở được:

```bash
curl -I https://staging.c2-app-005.quangtm.site
```

5. API mở được:

```bash
curl https://staging.c2-app-005.quangtm.site/openapi.json
```

6. Browser test:

- Homepage.
- Login/register user.
- Admin login.
- Contact form.
- Chat AI.

## 11. Quy trình sau khi có CD tự động

Quy trình mới:

```text
Developer code
  ↓
Push feature branch
  ↓
Pull Request vào dev
  ↓
Review + merge
  ↓
CI chạy
  ↓
Docker image publish
  ↓
Staging deploy tự động
  ↓
Mentor xem link staging
```

Không cần SSH thủ công mỗi lần deploy nếu pipeline pass.

## 12. Quyết định cần duyệt

Trước khi thực hiện, cần xác nhận:

1. Có dùng SSH deploy tự động từ GitHub Actions vào VPS không?
2. Dùng user `root` tạm thời hay tạo user riêng `deploy`?
3. Có dùng `appleboy/ssh-action` không, hay muốn tự viết `ssh` command thuần?
4. Có chấp nhận deploy tự động mỗi khi merge/push vào `dev` không?

Đề xuất của tôi:

```text
Version đầu dùng root + appleboy/ssh-action để nhanh ổn định.
Sau đó hardening bằng user deploy riêng.
```

