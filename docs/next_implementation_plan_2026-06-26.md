# Phương án triển khai tiếp theo — sau audit 26/06/2026

## 1. Mục tiêu của giai đoạn tiếp theo

Giai đoạn tiếp theo không nên tập trung thêm nhiều feature mới. Mục tiêu chính là:

```text
Sửa AI chat 500, sau đó làm cho Agent, Dashboard, Lead, Conversation và Database dùng chung một kiến trúc thống nhất.
```

Sau khi thống nhất, dự án mới nên tiếp tục:

- hoàn thiện AI UX,
- thêm streaming/RAG nâng cao,
- setup Cloudflare/HTTPS production,
- hardening CI/CD.

## 2. Nguyên tắc triển khai

1. Không làm mất staging hiện tại.
2. Không xóa model/API cũ ngay nếu chưa có migration an toàn.
3. Mỗi nhóm thay đổi phải có report riêng.
4. Mỗi bước phải có cách test rõ ràng.
5. Ưu tiên sửa kiến trúc nền trước feature mới.

## 3. Roadmap đề xuất

## Phase 1 — Architecture reconciliation

## Phase 0 — Fix AI chat 500 on staging

### Mục tiêu

Đưa `/agent/chat` từ trạng thái lỗi HTTP 500 về trạng thái usable.

### Công việc

1. Lấy log backend trên VPS:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs backend --tail 300
```

2. Test trực tiếp từ VPS:

```bash
curl -i -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Tôi muốn mua căn 2PN khoảng 3 tỷ để ở, nên chọn phân khu nào?"}],"session_id":"manual-test-ai-500"}'
```

3. Kiểm tra trạng thái provider:

```bash
curl http://localhost:8000/agent/status
```

4. Phân loại lỗi:

- thiếu/sai `OPENROUTER_API_KEY`
- sai `OPENROUTER_MODEL`
- sai `OPENROUTER_BASE_URL`
- VPS không gọi được OpenRouter
- lỗi DB do Agent đang dùng schema async riêng
- lỗi migration/table mismatch
- lỗi runtime trong `agent_routes.py`, `llm_node.py`, `rag_node.py`

5. Chỉ sau khi có log cụ thể mới sửa code.

### Kết quả mong đợi

```text
POST /agent/chat → HTTP 200
```

và frontend chat nhận được `response`.

### Lưu ý

Phase này là P0 vì nếu AI chưa chat được thì chưa nên refactor hay thêm feature AI lớn.

### Mục tiêu

Hợp nhất Agent với database/dashboard hiện có.

### Công việc

1. Chọn một schema chính:

```text
src.db.base.Base
src.db.session
src.models.entities
```

2. Refactor `/agent/chat` để dùng:

```text
entities.Conversation
entities.Message
```

thay vì:

```text
src.models.chat.Conversation
src.models.chat.Message
```

3. Chuẩn hóa field message:

Hiện dashboard dùng:

```text
sender = customer / ai / system
```

Agent dùng:

```text
role = user / assistant / system
```

Đề xuất mapping:

| Agent role | DB sender |
| --- | --- |
| user | customer |
| assistant | ai |
| system | system |

4. Refactor lead scoring/contact flow để dashboard và AI cùng đọc một bảng `leads`.

5. Quyết định giữ hay loại bỏ các model song song:

```text
src.models.chat
src.models.lead
src.models.property
src.database
```

Không xóa ngay; trước tiên đánh dấu deprecated hoặc ngừng sử dụng runtime.

### Kết quả mong đợi

- Chat AI xuất hiện trong Admin Conversations.
- Lead từ form public và lead từ AI/handover đều xuất hiện trong cùng Admin Leads.
- Không còn hai định nghĩa khác nhau cho Conversation/Message/Lead trong luồng runtime chính.

### Test

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
cd FE
npm run build
```

Manual staging test:

1. Mở website.
2. Chat với AI.
3. Vào Admin → Conversations.
4. Thấy user message và AI message.
5. Gửi form lead.
6. Vào Admin → Leads.
7. Lead có đúng thông tin và có liên kết session/chat nếu có.

## Phase 2 — LLM provider verification

### Mục tiêu

Đảm bảo OpenRouter/OpenAI/custom gateway hoạt động thật trên staging.

### Công việc

1. Chốt `.env` provider:

OpenRouter:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=<secret>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=<exact-openrouter-model-id>
```

OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=<secret>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

2. Test endpoint:

```bash
curl http://localhost:8000/agent/status
```

3. Test chat:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Tôi muốn mua căn 2PN khoảng 3 tỷ để ở, nên chọn phân khu nào?"}],"session_id":"manual-test-openrouter"}'
```

4. Log lỗi model/key/base URL nếu có.

### Kết quả mong đợi

```json
"llm_configured": true
```

và chat trả lời bằng AI thật.

## Phase 3 — Handover UX and lead capture integration

### Mục tiêu

Khi AI phát hiện khách cần Sales, UI phải dẫn khách để lại thông tin một cách tự nhiên.

### Công việc

1. Frontend đọc `trigger_handover`.
2. Khi `true`, Chat Widget hiển thị mini lead form hoặc CTA rõ:

```text
Để Sales kiểm tra quỹ căn/giá chốt, Anh/Chị để lại số điện thoại tại đây.
```

3. Submit lead kèm:

```text
session_id
chat_history
recommended_zone
user_profile nếu có
```

4. Dashboard hiển thị:

- lead source = ai_chat
- session id
- chat transcript
- AI recommendation/score

### Test

1. Chat: “Tôi muốn đặt cọc căn R1.01”.
2. AI trả handover.
3. Form xuất hiện.
4. Gửi số điện thoại.
5. Dashboard có lead mới và xem được hội thoại.

## Phase 4 — Catalog schema cleanup

### Mục tiêu

Làm sạch code theo quyết định mới: **không dùng thiết kế `project -> zone -> subzone -> building`**.

### Công việc

1. Chốt schema catalog chính:

```text
subdivisions
apartment_specs
amenities
sales_policies
```

2. Rà soát các file còn dấu vết hierarchy cũ:

```text
src/models/property.py
docs/DATABASE_DESIGN_VINHOMES_AI_ADVISOR.md
README.md
ARCHITECTURE.md
```

3. Quyết định:

- giữ lại như tài liệu tham khảo cũ, hoặc
- đánh dấu deprecated, hoặc
- xóa khỏi runtime/import nếu không dùng.

4. Điều chỉnh Agent/RAG để gọi dữ liệu theo `subdivisions`/cleaned catalog thay vì mở rộng theo hierarchy cũ.

### Kết quả mong đợi

- Thành viên khác không phát triển nhầm theo hierarchy đã bỏ.
- Tài liệu và runtime thống nhất quanh `subdivisions`.

## Phase 5 — DevOps hardening

### Mục tiêu

Ổn định CI/CD và chuẩn bị HTTPS/production.

### Công việc

1. Sửa `docker-compose.https.yml` để đồng bộ DATABASE_URL có password.
2. Điều tra lỗi buildx:

```text
rpc error: code = Unavailable
error reading from server: EOF
graceful_stop
```

3. Nếu lỗi lặp lại, chọn một trong hai:

- bỏ `type=gha` cache tạm thời;
- tách backend/frontend Docker build thành hai job;
- dùng buildx command thủ công để log rõ hơn;
- cleanup builder/cache trước build.

4. Test HTTPS staging với Caddy/Cloudflare.
5. Test backup/restore thật trên staging.

## Phase 6 — Production readiness

### Mục tiêu

Chuẩn bị production một cách kiểm soát.

### Checklist

- Không còn default password trong UI.
- `.env.production` không placeholder.
- JWT secret mạnh.
- Admin password mạnh.
- LLM key không commit.
- CORS chỉ domain production.
- Port public chỉ 80/443.
- Backup/restore test pass.
- Rollback image test pass.
- Logs không lộ PII/API key.
- Có runbook xử lý sự cố.

## 4. Thứ tự ưu tiên đề xuất

| Ưu tiên | Việc cần làm | Lý do |
| --- | --- | --- |
| P0 | Sửa `/agent/chat` HTTP 500 trên staging | AI chưa usable, chặn mục tiêu cốt lõi |
| P0 | Hợp nhất DB/model cho Agent và Dashboard | Chặn rủi ro kiến trúc lớn nhất |
| P0 | Verify OpenRouter/OpenAI trên staging | AI là core value của project |
| P1 | Handover → Lead → Dashboard end-to-end | Biến chat thành lead thật |
| P1 | Sửa compose HTTPS DATABASE_URL | Tránh lỗi lặp khi chuyển domain |
| P1 | Ổn định Docker buildx CI | Tránh block deploy mỗi lần push |
| P2 | Streaming chat | UX tốt hơn nhưng không chặn core |
| P2 | Vector/semantic RAG | Nâng chất lượng AI sau khi data flow ổn |

## 5. Phiên bản đề xuất tiếp theo

### v0.9.0 — Agent integration hardening

Phạm vi:

- Sửa lỗi `/agent/chat` 500 trên staging.
- Refactor Agent dùng chung conversation/lead schema với dashboard.
- AI message hiện trong Admin Conversations.
- Handover chat có đường dẫn tạo lead.
- LLM provider status/test ổn định.

Không nên làm trong v0.9.0:

- Không quay lại thiết kế `project -> zone -> subzone -> building`.
- Không thêm streaming.
- Không thêm multi-agent.
- Không làm production domain nếu staging AI chưa ổn.

### v0.9.1 — DevOps stabilization

Phạm vi:

- Sửa compose HTTPS.
- Ổn định Docker buildx.
- Thêm deploy smoke test.
- Hoàn thiện staging HTTPS.

### v1.0.0-rc — Production candidate

Phạm vi:

- Remove demo credentials.
- Production `.env` validation.
- Backup/restore tested.
- Rollback tested.
- Cloudflare HTTPS.
- Mentor demo checklist.

## 6. Điều mình đề xuất bạn xác nhận

Trước khi mình triển khai tiếp, bạn nên xác nhận 3 quyết định:

1. Có đồng ý chọn `src.models.entities` + Alembic hiện tại làm schema chính không?
2. Có đồng ý refactor Agent để ghi vào Admin Conversations hiện tại không?
3. Có xác nhận chính thức bỏ hướng `project -> zone -> subzone -> building` và giữ `subdivisions` làm catalog schema chính không?

Sau khi bạn xác nhận, mình sẽ bắt đầu v0.9.0 theo từng bước nhỏ, mỗi bước có report riêng như quy ước.
