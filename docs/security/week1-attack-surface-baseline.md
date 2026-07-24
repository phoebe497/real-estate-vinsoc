# Week 1 attack-surface baseline

Ngày đánh giá: 24/07/2026  
Phạm vi: source code hiện tại, stack DAST local cô lập và deployment AWS EC2
thuộc dự án.

## 1. Tài sản và entry point

| Lớp | Bề mặt chính | Dữ liệu/đặc quyền |
| --- | --- | --- |
| Public frontend | `/`, `/chung-cu`, `/phan-khu`, `/phan-khu/[slug]` | Nội dung dự án, session chat |
| Admin frontend | `/admin/login`, dashboard, customers, sales, permissions, fallback rules | JWT, PII khách hàng, RBAC |
| Public API | `/health`, `/ready`, `/docs`, `/openapi.json`, catalog/zone, customer capture | Metadata hệ thống, lead PII |
| AI API | `/agent/chat`, `/agent/recommend`, `/agent/status` | Prompt, lịch sử chat, LLM/RAG context |
| Privileged API | auth, customers, sales, dashboard, permissions, fallback rules, customer score | JWT, role/permission, dữ liệu CRM |
| Data/service | PostgreSQL, GHCR, OpenRouter/OpenAI-compatible provider | PII, credentials, image artifacts, model input/output |

Các nhóm API được mount qua `/api/v1`, `/agent`, `/health` và `/ready`.
Swagger/OpenAPI giúp kiểm kê endpoint nhưng cũng cung cấp thông tin hữu ích cho
kẻ tấn công, vì vậy cần quyết định rõ có công khai `/docs` ở production hay
không.

## 2. Trust boundary và luồng dữ liệu

```text
Internet
  -> Caddy :80/:443
     -> Next.js frontend
     -> FastAPI backend
        -> PostgreSQL (private Docker network)
        -> LLM/embedding provider (outbound)

GitHub Actions
  -> GitHub OIDC
  -> scoped AWS IAM role
  -> fixed AWS SSM document
  -> EC2 deploy wrapper
  -> digest-pinned GHCR images
```

Chỉ Caddy publish 80/443. Port 3000, 8000 và 5432 không được mở trực tiếp.
Development và production là hai Compose project/volume riêng nhưng cùng kernel,
Docker daemon, EBS và failure domain; đây là cô lập vận hành, không phải security
boundary cấp host.

## 3. Kết quả baseline

### Semgrep SAST

- Image: `semgrep/semgrep:1.169.0`.
- Ruleset: `p/owasp-top-ten`.
- Phạm vi: `src/` và `FE/src/`.
- Kết quả local gần nhất: 84 files, 224 rules, parse 100%, 0 findings, 0 errors.

“0 findings” chỉ có nghĩa ruleset này không match source tại thời điểm scan,
không chứng minh ứng dụng không có lỗ hổng hoặc business-logic flaw.

### OWASP ZAP DAST

- Image: `zaproxy/zap-stable:2.17.0`.
- Frontend: 4 loại alert, 20 instances.
- Backend Swagger: 6 loại alert, 7 instances.
- Tổng sau chuẩn hóa: 27 instances gồm 14 medium, 7 low và 6 informational.

Các loại alert quan trọng:

- Content Security Policy chưa được thiết lập;
- thiếu anti-clickjacking header trên backend Swagger;
- thiếu Subresource Integrity cho tài nguyên ngoài;
- frontend lộ `X-Powered-By`;
- thiếu `X-Content-Type-Options` ở phản hồi backend được scan;
- tải JavaScript cross-domain.

Caddy đã thêm HSTS, `X-Content-Type-Options` và Referrer Policy ở môi trường
AWS. Baseline local đi trực tiếp vào container nên một số header tại edge không
xuất hiện; cần scan lại URL staging để xác nhận control ở toàn chuỗi.

## 4. Ưu tiên rủi ro

| Ưu tiên | Rủi ro | Hành động đề xuất |
| --- | --- | --- |
| P1 | Authorization/IDOR trên customer, sales, permissions | Test ma trận role và object ownership thủ công + integration test |
| P1 | Prompt injection/PII gửi sang provider | Duy trì guardrail, log sanitizer; review dữ liệu outbound |
| P1 | Dev/prod cùng EC2 | Giới hạn resource/IAM; lập ngưỡng tách host/RDS |
| P2 | CSP/clickjacking/SRI/header leakage | Áp CSP theo report-only trước, `frame-ancestors`, tắt powered-by |
| P2 | Public Swagger/OpenAPI | Hạn chế ở production hoặc yêu cầu authentication |
| P2 | Secret/image supply chain | OIDC ngắn hạn, image digest, rotation và SBOM/signing tiếp theo |

## 5. Giới hạn của baseline

- ZAP mới chạy passive baseline trên local stack; chưa active scan staging.
- Backend scan target là Swagger UI, chưa gọi mọi OpenAPI operation.
- Chưa có authenticated DAST theo từng role và chưa test IDOR/business rules.
- Chưa có dependency/container/IaC scan trong Week 1.
- Data lake hiện là artifact JSONL 30 ngày, chưa phải S3/SIEM lưu trữ dài hạn.

Đây là các gap có chủ đích cần đưa vào backlog, không được diễn giải thành phạm
vi đã hoàn thành.
