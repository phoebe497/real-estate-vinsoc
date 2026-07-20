# LLM provider design: OpenRouter, OpenAI and custom gateways

## Mục tiêu

Thiết kế backend để có thể đổi nhà cung cấp LLM bằng `.env`, không cần sửa code.

Các provider được hỗ trợ:

- OpenRouter
- OpenAI chính thức
- Gateway bất kỳ tương thích OpenAI API

## File đã cập nhật

- `src/config.py`
- `src/services/llm.py`
- `src/agents/nodes/llm_node.py`
- `src/api/agent_routes.py`
- `.env.staging.example`

## Cách cấu hình OpenRouter

Trong `.env` trên VPS:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=<your-openrouter-api-key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=<exact-openrouter-model-id>
OPENROUTER_SITE_URL=http://103.149.87.83:3000
OPENROUTER_APP_NAME=Ocean Park AI Advisor
```

Với model DeepSeek V4 Flash, cần copy đúng model slug từ OpenRouter.

Ví dụ format model thường có dạng:

```text
provider/model-name
```

Không nên đoán tên model nếu chưa copy từ OpenRouter model page.

## Cách cấu hình OpenAI chính thức

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

## Cách cấu hình gateway custom

```env
LLM_PROVIDER=custom
LLM_API_KEY=<provider-api-key>
LLM_BASE_URL=<provider-openai-compatible-base-url>
LLM_MODEL=<provider-model-id>
```

## Backward compatibility

Các biến cũ vẫn hoạt động:

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=
```

Tuy nhiên, từ giai đoạn staging trở đi nên dùng nhóm biến rõ provider hơn:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

## Cách kiểm tra trên VPS

Sau khi sửa `.env`, restart backend:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml up -d --force-recreate backend
```

Kiểm tra trạng thái agent:

```bash
curl http://localhost:8000/agent/status
```

Kết quả mong đợi:

```json
{
  "llm_provider": "openrouter",
  "llm_configured": true,
  "llm_model": "<exact-openrouter-model-id>",
  "llm_base_url": "https://openrouter.ai/api/v1"
}
```

Test chat:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Tôi muốn mua căn 2PN khoảng 3 tỷ để ở, nên chọn phân khu nào?"}],"session_id":"manual-test-openrouter"}'
```

Nếu response vẫn báo AI chưa cấu hình, kiểm tra lại key/model/base URL.

Nếu HTTP 500, xem log:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml logs backend --tail 200
```

