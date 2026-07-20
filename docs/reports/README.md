# Báo cáo triển khai theo phiên bản

Từ phiên bản `v0.1.0`, mỗi phiên bản của dự án có một báo cáo độc lập. Báo cáo không ghi đè lịch sử của phiên bản trước.

| Phiên bản | Nội dung chính | Báo cáo |
|---|---|---|
| `v0.1.0` | Nền tảng Database, Backend API và Public Frontend trước AI | [version-0.1.0-foundation.md](version-0.1.0-foundation.md) |
| `v0.2.0` | Authentication, RBAC và Sales Dashboard | [version-0.2.0-sales-dashboard.md](version-0.2.0-sales-dashboard.md) |
| `v0.2.1` | Sửa trạng thái sai sau khi gửi form tư vấn | [version-0.2.1-contact-form-fix.md](version-0.2.1-contact-form-fix.md) |
| `v0.3.0` | Conversation layer và lịch sử hội thoại trước AI | [version-0.3.0-conversation-layer.md](version-0.3.0-conversation-layer.md) |
| `v0.9.0` | Sửa AI chat HTTP 500 và đồng bộ lịch sử chat với lead/session | [version-0.9.0-agent-chat-stabilization.md](version-0.9.0-agent-chat-stabilization.md) |
| `v0.9.1` | Sửa AI data adapter và thêm chunk-based RAG từ `cleaned_data` | [version-0.9.1-ai-data-rag-adapter.md](version-0.9.1-ai-data-rag-adapter.md) |
| `v0.9.2` | Feedback data, chat và admin fixes | [version-0.9.2-feedback-data-chat-admin-fixes.md](version-0.9.2-feedback-data-chat-admin-fixes.md) |
| `v0.9.3` | Customer auth, session và CRM | [version-0.9.3-customer-auth-session-crm.md](version-0.9.3-customer-auth-session-crm.md) |
| `v0.9.4` | AI chat citation/fallback fix | [version-0.9.4-ai-chat-citation-fallback-fix.md](version-0.9.4-ai-chat-citation-fallback-fix.md) |
| `v0.9.5` | Chat flow, UI và security fix | [version-0.9.5-chat-flow-ui-security-fix.md](version-0.9.5-chat-flow-ui-security-fix.md) |
| `v0.9.6` | Deterministic AI advisory và RAG contract | [version-0.9.6-deterministic-ai-advisory-rag-contract.md](version-0.9.6-deterministic-ai-advisory-rag-contract.md) |
| `v0.9.7` | Rebuild public UI theo Next.js data-driven, navy/gold visual system và chat widget mới | [version-0.9.7-nextjs-public-ui-rebuild.md](version-0.9.7-nextjs-public-ui-rebuild.md) |

## Quy ước cho các phiên bản tiếp theo

Mỗi report mới phải có tối thiểu:

1. Mục tiêu và phạm vi phiên bản.
2. Công việc đã thực hiện.
3. Phương án kỹ thuật và lý do lựa chọn.
4. Thay đổi Database/API/UI.
5. Hướng dẫn cài đặt và sử dụng.
6. Hướng dẫn kiểm thử tự động và thủ công.
7. Kết quả xác minh thực tế.
8. Giới hạn và công việc của phiên bản tiếp theo.

Tên file sử dụng định dạng:

```text
docs/reports/version-X.Y.Z-short-description.md
```
