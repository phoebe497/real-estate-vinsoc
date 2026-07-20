# DevOps implementation reports

Thư mục này lưu báo cáo riêng cho từng phiên bản DevOps của dự án.

| Phiên bản | Nội dung | Trạng thái |
| --- | --- | --- |
| [0.3.1](version-0.3.1-security-environment.md) | Security và environment baseline | Hoàn thành |
| [Hotfix Docker Compose backend startup](hotfix-docker-compose-backend-startup.md) | Sửa lỗi backend failed to start do DATABASE_URL/password PostgreSQL | Hoàn thành |
| [0.4.0](version-0.4.0-production-docker.md) | Production Docker baseline | Hoàn thành |
| [0.5.0](version-0.5.0-ci-container-registry.md) | CI và container registry | Hoàn thành |
| [0.6.0](version-0.6.0-vps-staging-deployment.md) | VPS staging deployment | Hoàn thành |
| [0.7.0](version-0.7.0-cloudflare-https.md) | Cloudflare, HTTPS và reverse proxy | Hoàn thành |
| [0.8.0](version-0.8.0-production-release-backup-rollback.md) | Production release, backup và rollback | Hoàn thành |
| [CI runner strategy](ci-runner-strategy-after-dev-merge.md) | Hướng xử lý self-hosted runner và Docker publish sau khi merge vào dev | Hoàn thành |
| [Manual platform actions](manual-platform-actions-checklist.md) | Checklist các bước user phải tự thực hiện trên GitHub, VPS, GHCR và Cloudflare | Hoàn thành |
| [GHCR publish success](ghcr-publish-success-next-steps.md) | Ghi nhận Docker publish đã pass và hướng dẫn deploy staging từ GHCR | Hoàn thành |
| [Hotfix staging backend unhealthy](hotfix-staging-backend-unhealthy.md) | Sửa cấu hình DATABASE_URL khi backend staging không healthy | Hoàn thành |
| [Hotfix browser randomUUID on HTTP staging](hotfix-browser-randomuuid-http-staging.md) | Sửa lỗi frontend crash khi mở staging bằng IP/HTTP do `crypto.randomUUID` không khả dụng | Hoàn thành |
| [Hotfix frontend localhost API URL](hotfix-frontend-api-url-localhost-cors.md) | Sửa lỗi frontend gọi `localhost:8000` khi chạy staging bằng IP VPS | Hoàn thành |
| [Hotfix AI not configured](hotfix-agent-ai-not-configured.md) | Rà soát lỗi staging chạy được nhưng AI chat chưa hoạt động do thiếu/cấu hình sai LLM key | Hoàn thành |
| [LLM provider design](llm-provider-openrouter-openai-design.md) | Thiết kế cấu hình để đổi giữa OpenRouter, OpenAI và gateway OpenAI-compatible bằng `.env` | Hoàn thành |

Mỗi báo cáo trình bày công việc, phương án kỹ thuật, kết quả, hướng dẫn sử dụng và cách kiểm thử.
