"""Embedding provider abstraction."""

from __future__ import annotations

import sys

from skillport.shared.config import Config


def _openai_embedding(
    text: str,
    *,
    api_key: str | None,
    model: str,
    base_url: str | None = None,
) -> list[float]:
    if not api_key and base_url:
        api_key = "sk-local"
    # Prefer OpenAI v1+/v2 client; fall back to legacy SDK if unavailable.
    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        OpenAI = None  # type: ignore

    if OpenAI:
        client_kwargs: dict[str, str] = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)
        resp = client.embeddings.create(input=[text], model=model)
        return resp.data[0].embedding

    import openai  # lazy import for legacy <1.x

    if api_key:
        openai.api_key = api_key
    if base_url:
        openai.api_base = base_url
        try:
            openai.base_url = base_url
        except Exception:
            pass
    resp = openai.Embedding.create(input=[text], model=model)
    return resp["data"][0]["embedding"]


def get_embedding(text: str, config: Config) -> list[float] | None:
    """Fetch embedding according to provider; returns None when provider='none'."""
    provider = config.embedding_provider
    text = text.replace("\n", " ")

    if provider == "none":
        return None

    try:
        if provider == "openai":
            vec = _openai_embedding(
                text,
                api_key=config.openai_api_key,
                model=config.openai_embedding_model,
            )
            return vec

        if provider in {
            "openai_compatible",
            "dashscope",
            "zhipu",
            "baidu",
            "tencent",
            "local",
        }:
            vec = _openai_embedding(
                text,
                api_key=config.embedding_api_key,
                model=config.embedding_model or "",
                base_url=config.embedding_base_url,
            )
            return vec

        raise ValueError(f"Unsupported embedding_provider: {provider}")
    except Exception as exc:
        print(f"Embedding error ({provider}): {exc}", file=sys.stderr)
        if provider == "local":
            print(
                "Local embeddings unavailable; falling back to full-text search.",
                file=sys.stderr,
            )
            return None
        raise


__all__ = ["get_embedding"]
