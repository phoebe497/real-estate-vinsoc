# Hotfix: staging deployed but AI chat is not working

## Bối cảnh

Staging đã deploy thành công lên VPS, frontend/backend/database đều chạy được, nhưng chat AI không trả lời như kỳ vọng.

Frontend gọi endpoint:

```text
POST /agent/chat
```

Backend route tồn tại tại:

```text
src/api/agent_routes.py
```

Luồng xử lý:

```text
ChatWidget → /agent/chat → LangGraph agent → llm_node → OpenAI-compatible gateway
```

## Nguyên nhân khả nghi nhất

Trong template staging:

```env
OPENAI_API_KEY=
LANGCHAIN_TRACING_V2=false
```

Nếu VPS `.env` cũng đang để `OPENAI_API_KEY` rỗng, các intent cần gọi LLM sẽ không thể sinh câu trả lời AI thật.

Ngoài ra, trước hotfix này, `llm_node` gọi:

```py
llm = get_llm(...)
```

ở ngoài vùng `try`. Nếu `OPENAI_API_KEY` thiếu/sai và `ChatOpenAI` lỗi khi khởi tạo, backend có thể trả HTTP 500 cho `/agent/chat`.

Frontend khi đó chỉ hiện thông báo chung:

```text
Xin lỗi, hệ thống đang bận...
```

## Phương án đã áp dụng

### 1. Không để thiếu key làm crash agent

Cập nhật:

```text
src/agents/nodes/llm_node.py
```

Nếu `OPENAI_API_KEY` rỗng, agent trả về thông báo rõ ràng:

```text
Tính năng AI chưa được cấu hình trên môi trường staging...
```

Thay vì làm route `/agent/chat` lỗi 500.

### 2. Thêm thông tin trạng thái LLM vào agent status

Cập nhật:

```text
src/api/agent_routes.py
```

Endpoint:

```text
GET /agent/status
```

trả thêm:

```json
{
  "llm_configured": true,
  "llm_model": "gpt-4o-mini",
  "llm_base_url": "https://api.freemodel.dev/v1"
}
```

Không trả `OPENAI_API_KEY`, chỉ trả boolean an toàn.

## Việc user cần kiểm tra trên VPS

Kiểm tra agent status:

```bash
curl http://localhost:8000/agent/status
```

Nếu thấy:

```json
"llm_configured": false
```

thì cần cấu hình key trong `.env`:

```bash
cd /opt/ocean-park-advisor
nano .env
```

Điền nếu dùng OpenRouter:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=<your-openrouter-api-key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=<exact-openrouter-model-id>
OPENROUTER_SITE_URL=http://103.149.87.83:3000
OPENROUTER_APP_NAME=Ocean Park AI Advisor
```

Ví dụ model id cần lấy đúng theo slug trên OpenRouter. Nếu model bạn muốn dùng là DeepSeek V4 Flash, hãy copy chính xác model id từ OpenRouter dashboard/model page và điền vào:

```env
OPENROUTER_MODEL=<deepseek-v4-flash-model-slug>
```

Nếu dùng OpenAI chính thức:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

Nếu dùng gateway OpenAI-compatible khác:

```env
LLM_PROVIDER=custom
LLM_API_KEY=<provider-api-key>
LLM_BASE_URL=<provider-openai-compatible-base-url>
LLM_MODEL=<provider-model-id>
```

Sau đó restart backend:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml up -d --force-recreate backend
```

Kiểm tra lại:

```bash
curl http://localhost:8000/agent/status
```

## Test chat trực tiếp trên VPS

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Tôi muốn mua căn 2PN khoảng 3 tỷ để ở, nên chọn phân khu nào?"}],"session_id":"manual-test-ai"}'
```

Kết quả tốt:

- HTTP 200.
- Có trường `response`.
- Không còn lỗi 500.
- Nếu key đúng, response là câu trả lời AI theo dữ liệu dự án.

Nếu response báo AI chưa cấu hình, nghĩa là backend chạy đúng nhưng `.env` chưa có key.

## Debug log backend

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs backend --tail 200
```

Các lỗi thường gặp:

- thiếu `OPENAI_API_KEY`
- thiếu `OPENROUTER_API_KEY` nếu dùng OpenRouter
- key sai/hết hạn
- `OPENAI_BASE_URL` / `OPENROUTER_BASE_URL` / `LLM_BASE_URL` không đúng
- VPS không gọi được gateway bên ngoài
- model không được gateway hỗ trợ

## Thiết kế provider-agnostic

Backend hiện hỗ trợ 3 chế độ qua `.env`:

| Provider | Biến chính | Base URL mặc định | Ghi chú |
| --- | --- | --- | --- |
| OpenRouter | `LLM_PROVIDER=openrouter`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` | `https://openrouter.ai/api/v1` | Phù hợp dùng DeepSeek, Qwen, Claude, Gemini... qua OpenRouter |
| OpenAI | `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_MODEL` | `https://api.openai.com/v1` | Dùng OpenAI chính thức |
| Custom | `LLM_PROVIDER=custom`, `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | Không có | Dùng mọi gateway tương thích OpenAI |

Các biến `OPENAI_*` cũ vẫn được giữ để không phá deploy cũ.
