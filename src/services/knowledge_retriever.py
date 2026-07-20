"""Keyword/chunk retriever for AI Agent RAG.

This is intentionally not a vector database yet. It uses the reviewed
`ai_knowledge_chunks.json` file and retrieves chunks by subdivision slug,
topic and keyword overlap so the Agent can answer from the new cleaned data.
"""

from __future__ import annotations

import re
import unicodedata

from src.services.vinhomes_data import load_knowledge_chunks

TOPIC_KEYWORDS = {
    "apartment_specs": [
        "giá",
        "gia",
        "bao nhiêu",
        "bao nhieu",
        "căn",
        "can",
        "studio",
        "1pn",
        "2pn",
        "3pn",
        "diện tích",
        "dien tich",
    ],
    "internal_amenities": [
        "tiện ích nội khu",
        "tien ich noi khu",
        "nội khu",
        "noi khu",
        "bể bơi",
        "be boi",
        "gym",
        "vườn",
        "vuon",
        "sảnh",
        "sanh",
    ],
    "external_amenities": [
        "tiện ích ngoại khu",
        "tien ich ngoai khu",
        "ngoại khu",
        "ngoai khu",
        "vincom",
        "vinuni",
        "vinschool",
        "vinmec",
        "trường",
        "truong",
        "bệnh viện",
        "benh vien",
    ],
    "sales_policies": [
        "chính sách",
        "chinh sach",
        "vay",
        "lãi suất",
        "lai suat",
        "chiết khấu",
        "chiet khau",
        "thanh toán",
        "thanh toan",
        "voucher",
        "quà tặng",
        "qua tang",
    ],
    "location": [
        "vị trí",
        "vi tri",
        "ở đâu",
        "o dau",
        "đường",
        "duong",
        "gần",
        "gan",
        "xa",
        "kết nối",
        "ket noi",
    ],
    "overview": [
        "tổng quan",
        "tong quan",
        "giới thiệu",
        "gioi thieu",
        "quy mô",
        "quy mo",
        "chủ đầu tư",
        "chu dau tu",
    ],
}

STOPWORDS = {
    "toi",
    "tôi",
    "co",
    "có",
    "la",
    "là",
    "ve",
    "về",
    "cho",
    "hoi",
    "hỏi",
    "muon",
    "muốn",
    "can",
    "cần",
    "khong",
    "không",
    "duoc",
    "được",
    "phan",
    "phân",
    "khu",
}


def normalize_text(value: str) -> str:
    """Lowercase and strip Vietnamese accents for forgiving keyword matching."""
    value = value.lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    return value.replace("đ", "d")


def tokenize(value: str) -> set[str]:
    normalized = normalize_text(value)
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalized)
        if len(token) >= 2 and token not in STOPWORDS
    }


def detect_topics(query: str) -> set[str]:
    normalized = normalize_text(query)
    topics: set[str] = set()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(normalize_text(keyword) in normalized for keyword in keywords):
            topics.add(topic)
    return topics


def detect_subdivision_slugs(query: str) -> set[str]:
    """Detect mentioned subdivision slugs/names from loaded chunks."""
    normalized_query = normalize_text(query)
    detected: set[str] = set()
    for chunk in load_knowledge_chunks():
        slug = chunk.get("subdivision_slug", "")
        name = chunk.get("subdivision_name", "")
        slug_phrase = normalize_text(slug.replace("-", " "))
        name_phrase = normalize_text(name)

        if slug and (slug in normalized_query or slug_phrase in normalized_query or name_phrase in normalized_query):
            detected.add(slug)
            continue

        # Helpful short aliases: "zenpark", "sapphire", "masteri waterfront", ...
        slug_tokens = [token for token in slug_phrase.split() if token not in {"the"}]
        if slug_tokens and all(token in normalized_query for token in slug_tokens):
            detected.add(slug)
    return detected


def retrieve_knowledge_chunks(query: str, max_chunks: int = 5) -> list[dict]:
    """Retrieve relevant knowledge chunks by slug/topic/keyword overlap."""
    chunks = load_knowledge_chunks()
    if not chunks:
        return []

    query_tokens = tokenize(query)
    detected_slugs = detect_subdivision_slugs(query)
    detected_topics = detect_topics(query)

    scored: list[tuple[int, dict]] = []
    for chunk in chunks:
        score = 0
        slug = chunk.get("subdivision_slug", "")
        topic = chunk.get("topic", "")
        content = chunk.get("content", "")
        name = chunk.get("subdivision_name", "")

        if detected_slugs and slug in detected_slugs:
            score += 80
        elif not detected_slugs:
            score += len(query_tokens.intersection(tokenize(f"{slug} {name}"))) * 8

        if detected_topics and topic in detected_topics:
            score += 50
        elif not detected_topics and topic == "overview":
            score += 5

        score += len(query_tokens.intersection(tokenize(content))) * 3

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:max_chunks]]


def format_chunks_for_context(chunks: list[dict]) -> str:
    """Format retrieved chunks with source labels for the LLM context."""
    if not chunks:
        return ""

    lines = ["**Nguồn knowledge chunks liên quan:**"]
    for chunk in chunks:
        source = f"{chunk.get('subdivision_slug', '')}/{chunk.get('topic', '')}"
        lines.append(f"\n[source: {source}]\n{chunk.get('content', '')}")
    return "\n".join(lines)
