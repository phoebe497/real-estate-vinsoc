"""Embedding client helpers for pgvector-backed RAG."""

from __future__ import annotations

import hashlib
import logging
import math
import re

from langchain_openai import OpenAIEmbeddings

from src.config import get_settings

logger = logging.getLogger(__name__)


def _embedding_client_config() -> dict:
    settings = get_settings()
    if settings.rag_embedding_provider == "openrouter":
        return {
            "api_key": settings.openrouter_api_key,
            "base_url": settings.openrouter_base_url,
            "model": settings.openrouter_embedding_model,
        }
    return {
        "api_key": settings.openai_embedding_api_key or settings.openai_api_key,
        "base_url": settings.openai_embedding_base_url or settings.openai_base_url,
        "model": settings.openai_embedding_model,
    }


def get_embeddings_client() -> OpenAIEmbeddings:
    settings = get_settings()
    client_config = _embedding_client_config()
    kwargs = {
        "model": client_config["model"],
        "api_key": client_config["api_key"],
        "base_url": client_config["base_url"],
        "timeout": 30.0,
        "default_headers": {
            "HTTP-Referer": "https://vinhomes-ai.local",
            "X-Title": "Vinhomes AI Real Estate Advisor",
        },
    }
    if settings.openai_embedding_dimensions:
        kwargs["dimensions"] = settings.openai_embedding_dimensions
    return OpenAIEmbeddings(**kwargs)


async def embed_query(text: str) -> list[float]:
    if get_settings().rag_embedding_provider == "local_hash":
        return local_hash_embedding(text)
    client = get_embeddings_client()
    return await client.aembed_query(text)


async def try_embed_query(text: str) -> list[float] | None:
    try:
        return await embed_query(text)
    except Exception as exc:
        logger.warning(
            "query embedding failed; continuing without vector search",
            extra={"error_type": type(exc).__name__},
        )
        return None


async def embed_documents(texts: list[str]) -> list[list[float]]:
    if get_settings().rag_embedding_provider == "local_hash":
        return [local_hash_embedding(text) for text in texts]
    client = get_embeddings_client()
    return await client.aembed_documents(texts)


def local_hash_embedding(text: str) -> list[float]:
    """Deterministic local fallback embedding for pgvector bootstrapping.

    This is not a semantic model. Use provider embeddings for production quality.
    """
    settings = get_settings()
    dim = settings.openai_embedding_dimensions
    vector = [0.0] * dim
    tokens = re.findall(r"[a-zA-Z0-9À-ỹ]+", text.lower())
    features: list[str] = []
    features.extend(tokens)
    features.extend(" ".join(tokens[i : i + 2]) for i in range(max(0, len(tokens) - 1)))

    for feature in features:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
