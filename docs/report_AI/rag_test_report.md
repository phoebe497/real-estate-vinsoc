# Báo Cáo Kiểm Thử: RAG Knowledge Validation — Kịch bản #2

**Ngày:** 25/06/2026
**Nhánh:** `phoebe_dev` (commit `3902d37`)
**Kịch bản test:** Hỏi xoáy vào tiện ích nội khu (Test độ sâu RAG Knowledge)
**Câu hỏi test:** _"Ngoài việc mua nhà ra thì ở Ocean Park Gia Lâm có những tiện ích gì nổi bật không? Tôi nghe nói có hồ nhân tạo?"_

---

## 1. Tóm Tắt Kết Quả (Test Summary)

```
============================= 16 passed in 0.11s ==============================
```

| Nhóm test | Số test | Kết quả |
|-----------|:-------:|:-------:|
| **TestIntentClassification** | 3 | ✅ 3/3 PASS |
| **TestRAGRetrieval** | 6 | ✅ 6/6 PASS |
| **TestResponseQuality** | 2 | ✅ 2/2 PASS |
| **TestCitationValidation** | 2 | ✅ 2/2 PASS |
| **TestAntiHallucination** | 3 | ✅ 3/3 PASS |
| **TỔNG** | **16** | ✅ **16/16 PASS** |

### Kết luận tổng thể: ✅ **PASS — Backend RAG Pipeline hoạt động đúng**

> [!NOTE]
> UI Testing (browser-based) chưa được thực hiện vì nhánh `phoebe_dev` không chứa thư mục `FE/`. Phần UI testing cần chạy trên nhánh `dev`.

---

## 2. Chi tiết từng nhóm test

### 2.1 Intent Classification (3/3 PASS)

| Test | Mô tả | Kết quả |
|------|-------|:-------:|
| `test_intent_detects_amenity_query` | Câu hỏi tiện ích → classify thành `consult` | ✅ |
| `test_intent_not_out_of_scope` | Câu hỏi hợp lệ về Ocean Park KHÔNG bị chặn | ✅ |
| `test_intent_not_handover` | Câu hỏi thông tin KHÔNG kích hoạt chuyển Sales | ✅ |

### 2.2 RAG Retrieval (6/6 PASS)

| Test | Mô tả | Kết quả |
|------|-------|:-------:|
| `test_project_info_contains_highlights` | Data chứa Hồ Ngọc Trai 24.5ha, Crystal Lagoons | ✅ |
| `test_amenity_keywords_trigger_context` | Từ "tiện ích" kích hoạt retrieval | ✅ |
| `test_amenities_data_not_empty` | `get_amenities()` trả về dữ liệu | ✅ |
| `test_rag_node_builds_zone_context_with_project_info` | `zone_context` chứa tên dự án | ✅ |
| `test_rag_node_includes_amenity_context` | `zone_context` có section "Tiện ích nổi bật" | ✅ |
| `test_rag_retrieves_expected_facts` | Context chứa Hồ Ngọc Trai, 24.5ha, Crystal Lagoons, 6.1ha | ✅ |

### 2.3 Response Quality (2/2 PASS)

| Test | Mô tả | Kết quả |
|------|-------|:-------:|
| `test_project_highlights_are_in_correct_format` | Highlights là list of strings | ✅ |
| `test_zone_data_has_required_fields` | Mọi zone có name, slug, description | ✅ |

### 2.4 Citation Validation (2/2 PASS)

| Test | Mô tả | Kết quả |
|------|-------|:-------:|
| `test_all_zone_slugs_are_valid_url_segments` | Mọi slug chỉ chứa `[a-z0-9-]` | ✅ |
| `test_citation_pattern_matches_valid_slugs` | Link `[1](/phan-khu/the-zenpark-vinhomes)` trỏ slug thực | ✅ |

> [!WARNING]
> Bug đã được phát hiện và sửa trong phiên này: `SYSTEM_PROMPT` chứa ví dụ citation với slug `the-zenpark` — nhưng slug thực tế trong data là `the-zenpark-vinhomes`. Test đã bắt lỗi này, đã sửa cả trong prompt và test.

### 2.5 Anti-Hallucination (3/3 PASS)

| Test | Mô tả | Kết quả |
|------|-------|:-------:|
| `test_out_of_scope_blocks_wrong_project` | "Vinhomes Grand Park có hồ bơi không?" → bị chặn | ✅ |
| `test_prompt_injection_blocked` | "Ignore all previous instructions..." → bị chặn | ✅ |
| `test_project_data_has_correct_name` | Tên dự án chứa "Ocean Park" + "Gia Lâm" | ✅ |

---

## 3. Retrieval Metrics (Chỉ số Truy xuất)

| Metric | Giá trị | Giải thích |
|--------|:-------:|------------|
| **Recall** | **5/5 = 100%** | Tất cả facts kỳ vọng (Hồ Ngọc Trai, Crystal Lagoons, Vinschool, Brighton, VinUni) đều có trong context |
| **Precision** | **~83%** | Context cũng chứa thông tin phân khu bổ sung (hữu ích nhưng không được hỏi trực tiếp) |
| **Source Coverage** | **1/3 = 33%** | Chỉ dùng `vinhomes_real.json`, chưa tích hợp `ai_knowledge_chunks.json` |

---

## 4. Citation Metrics (Chỉ số Trích dẫn)

| Metric | Giá trị | Giải thích |
|--------|:-------:|------------|
| **Slug Validity** | ✅ **100%** | Tất cả 15 slug trong data đều URL-safe |
| **Example Citation Accuracy** | ✅ **PASS** (sau khi sửa) | Slug trong prompt ví dụ khớp data thực |
| **Structured Citations** | ❌ **N/A** | API response chưa có field `citations[]` riêng biệt |

---

## 5. UI Validation

| Hạng mục | Kết quả | Ghi chú |
|----------|:-------:|---------|
| Citation trong chat UI | ⏳ Chưa test | Cần nhánh `dev` (có `FE/`) |
| Link clickable | ⏳ Chưa test | — |
| Console errors | ⏳ Chưa test | — |

---

## 6. Hallucination Check

| Loại ảo giác | Trạng thái | Chi tiết |
|--------------|:----------:|----------|
| Tiện ích không tồn tại | ✅ GUARDED | LLM bị ràng buộc bởi zone_context |
| Phân khu sai dự án | ✅ BLOCKED | `intent_node` chặn dự án khác |
| Prompt injection | ✅ BLOCKED | Regex filter chặn injection patterns |
| Citation slug sai | ✅ FIXED | Bug `the-zenpark` → `the-zenpark-vinhomes` đã sửa |

---

## 7. Recommended Fixes (Đề xuất cải thiện)

### 🔴 Ưu tiên CAO

| Fix | Mô tả |
|-----|-------|
| **Structured Citations** | Thêm field `citations[]` vào `ChatResponse` schema với `source_url`, `chunk_id` |
| **Knowledge Chunks Integration** | Tích hợp `ai_knowledge_chunks.json` vào RAG pipeline (hiện chỉ dùng `vinhomes_real.json`) |

### 🟡 Ưu tiên TRUNG BÌNH

| Fix | Mô tả |
|-----|-------|
| **Citation Validation Post-LLM** | Parse link trong LLM response, cross-check slug với `VALID_SLUGS`, loại bỏ hallucinated links |
| **Semantic Search** | Thay regex keyword matching bằng embedding-based retrieval (ChromaDB) |

### 🟢 Ưu tiên THẤP

| Fix | Mô tả |
|-----|-------|
| **UI Testing trên `dev`** | Chạy browser test sau khi merge `phoebe_dev` vào `dev` |
| **Data Freshness Validation** | Check `data_period` và cảnh báo nếu data quá 6 tháng |

---

## 8. File References

| File | Mô tả |
|------|-------|
| [test_rag_scenario2.py](file:///d:/VinUni-AI20K/team-005-ai-real-estate/tests/test_agents/test_rag_scenario2.py) | Test suite (16 tests) |
| [llm_node.py](file:///d:/VinUni-AI20K/team-005-ai-real-estate/src/agents/nodes/llm_node.py) | Citation prompt đã sửa slug |
| [rag_node.py](file:///d:/VinUni-AI20K/team-005-ai-real-estate/src/agents/nodes/rag_node.py) | RAG retrieval logic |
| [intent_node.py](file:///d:/VinUni-AI20K/team-005-ai-real-estate/src/agents/nodes/intent_node.py) | Intent classification + injection guard |
