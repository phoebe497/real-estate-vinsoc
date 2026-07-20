# CI runner strategy after merging to dev

## Bối cảnh

Sau khi resolve conflict và thử push/merge vào branch `dev`, GitHub Actions hiện có trạng thái:

- Backend lint/tests đã chạy được.
- Frontend build đã chạy được.
- Docker build and publish vẫn còn lỗi.

Trước đó GitHub-hosted runner `ubuntu-latest` bị chặn bởi billing/spending limit:

```text
The job was not started because recent account payments have failed
or your spending limit needs to be increased.
```

Sau khi đổi Backend và Frontend sang `self-hosted`, hai job này đã chạy được CI.

## Kết luận hiện tại

Việc Backend/Frontend chạy được nghĩa là phần kiểm tra code cơ bản đã ổn hơn.

Docker build and publish còn lỗi không đồng nghĩa code BE/FE sai. Job Docker có yêu cầu môi trường cao hơn:

- Docker daemon phải chạy được.
- Docker Buildx phải có.
- Runner phải có quyền chạy Docker.
- GitHub token phải có quyền push GHCR.
- Package registry GHCR phải cho phép push.
- Nếu dùng GitHub-hosted runner thì billing/quota phải hợp lệ.

## Có nên đổi Docker job sang self-hosted không?

Không nên đổi vội nếu self-hosted runner là máy cá nhân/laptop.

Nên giữ chiến lược:

```yaml
backend-checks:
  runs-on: self-hosted

frontend-build:
  runs-on: self-hosted

docker-images:
  runs-on: ubuntu-latest
```

Lý do:

- Backend/frontend chỉ cần Python/Node, ít rủi ro.
- Docker publish cần quyền cao hơn và có thể tốn disk/network.
- GitHub-hosted runner sạch hơn cho build image và push registry.

Chỉ nên đổi Docker job sang `self-hosted` nếu runner là VPS/máy CI riêng, không phải máy cá nhân, và đã kiểm tra:

```bash
docker version
docker compose version
docker buildx version
```

## Nếu vẫn muốn dùng self-hosted cho Docker

Cần đảm bảo runner có:

1. Docker Engine đang chạy.
2. Docker Buildx hoạt động.
3. User chạy runner có quyền Docker.
4. Runner có network ổn định để pull base image và push GHCR.
5. Disk còn đủ dung lượng.
6. Workflow có quyền:

```yaml
permissions:
  contents: read
  packages: write
```

Nên thêm bước kiểm tra vào job Docker:

```yaml
- name: Verify Docker on runner
  run: |
    docker version
    docker buildx version
```

## Hướng xử lý khuyến nghị

### Phương án A - đúng chuẩn nhất

Sửa billing/quota GitHub Actions để Docker job tiếp tục dùng:

```yaml
runs-on: ubuntu-latest
```

Ưu điểm:

- Môi trường sạch.
- Ít phụ thuộc máy cá nhân.
- Phù hợp hơn với production CI/CD.

Nhược điểm:

- Cần owner repo/account xử lý Billing & plans.

### Phương án B - tạm thời để học/dev

Đổi Docker job sang:

```yaml
runs-on: self-hosted
```

Chỉ dùng nếu runner có Docker ổn định.

Ưu điểm:

- Không phụ thuộc GitHub-hosted runner billing.
- Có thể tiếp tục học flow GHCR.

Nhược điểm:

- Dễ lỗi quyền Docker.
- Dễ đầy disk.
- Runner offline thì CI/CD dừng.
- Cần cẩn thận bảo mật Docker socket/token.

## Checklist debug Docker build and publish

Khi Docker job lỗi, kiểm tra theo thứ tự:

### 1. Job có chạy hay bị chặn billing?

Nếu log là:

```text
The job was not started because recent account payments have failed
```

thì lỗi nằm ở GitHub billing, không nằm ở Dockerfile.

### 2. Docker có chạy trên runner không?

Log cần có:

```bash
docker version
docker buildx version
```

Nếu lỗi permission:

```text
permission denied while trying to connect to the Docker daemon
```

thì runner user chưa có quyền Docker.

### 3. GHCR login có thành công không?

Workflow dùng:

```yaml
permissions:
  packages: write
```

và login bằng:

```yaml
password: ${{ secrets.GITHUB_TOKEN }}
```

Nếu push fail 403, kiểm tra package permissions/repo visibility.

### 4. Image name có đúng không?

Workflow đang build:

```text
ghcr.io/<owner>/<repo>-backend:<tag>
ghcr.io/<owner>/<repo>-frontend:<tag>
```

Sau merge vào `dev`, tag mong đợi là:

```text
dev
sha-xxxxxxx
```

### 5. Frontend build arg có đúng không?

Docker frontend cần:

```yaml
NEXT_PUBLIC_API_URL
```

Nếu chưa set GitHub variable, workflow fallback:

```text
http://localhost:8000/api/v1
```

Tạm ổn cho build, nhưng staging thật nên set đúng URL API.

## Trạng thái mục tiêu hiện tại

Mục tiêu ngắn hạn:

- Pull Request không còn conflict.
- Backend CI pass.
- Frontend CI pass.
- Docker job lỗi được xác định là do runner/billing/quyền, không phải code.

Mục tiêu tiếp theo:

- Sửa Docker build and publish.
- Có image GHCR tag `dev`.
- VPS staging pull được image `dev`.

## Khuyến nghị hành động tiếp theo

1. Giữ Backend/Frontend ở `self-hosted` nếu hiện đang chạy ổn.
2. Tạm giữ Docker ở `ubuntu-latest`.
3. Nếu Docker vẫn bị billing block, trao đổi với owner repo để xử lý Billing & plans.
4. Nếu muốn bypass billing, chỉ đổi Docker sang `self-hosted` sau khi runner pass:

```bash
docker version
docker buildx version
```

5. Sau khi Docker job pass, kiểm tra GHCR Packages có:

```text
<repo>-backend:dev
<repo>-frontend:dev
```

