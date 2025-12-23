"""Set embedding provider and write env settings."""

from __future__ import annotations

import re
from pathlib import Path

import typer

from ..theme import console

ENV_LINE_RE = re.compile(r"^([A-Z0-9_]+)\s*=")

PROVIDERS = (
    "none",
    "local",
    "openai",
    "openai_compatible",
    "dashscope",
    "zhipu",
    "baidu",
    "tencent",
)

DEFAULTS = {
    "local": {
        "base_url": "http://localhost:11434/v1",
        "model": "bge-m3",
    },
    "dashscope": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "text-embedding-v3",
    },
}


def _format_env_value(value: str) -> str:
    if any(ch in value for ch in (' ', '#', '"')):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def _update_env_file(path: Path, updates: dict[str, str], removals: set[str]) -> None:
    lines: list[str] = []
    remaining = dict(updates)

    if path.exists():
        raw = path.read_text(encoding="utf-8").splitlines(keepends=True)
        for line in raw:
            match = ENV_LINE_RE.match(line.strip())
            if not match:
                lines.append(line)
                continue

            key = match.group(1)
            if key in removals:
                continue

            if key in remaining:
                lines.append(f"{key}={_format_env_value(remaining.pop(key))}\n")
            else:
                lines.append(line)

    if remaining:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] = lines[-1] + "\n"
        for key, value in remaining.items():
            lines.append(f"{key}={_format_env_value(value)}\n")

    path.write_text("".join(lines), encoding="utf-8")


def _require(value: str | None, label: str) -> str:
    if not value:
        raise typer.BadParameter(f"{label} is required for this provider.")
    return value


def set_embedding(
    provider: str = typer.Argument(..., help="Embedding provider"),
    base_url: str | None = typer.Option(None, "--base-url", help="Embedding base URL"),
    model: str | None = typer.Option(None, "--model", help="Embedding model name"),
    api_key: str | None = typer.Option(None, "--api-key", help="API key to store"),
    env_file: Path = typer.Option(
        Path(".env"),
        "--env-file",
        help="Env file to update (default: .env in current directory)",
    ),
):
    if provider not in PROVIDERS:
        raise typer.BadParameter(f"Unsupported provider '{provider}'.")

    updates: dict[str, str] = {}
    removals: set[str] = set()

    if provider == "none":
        updates["SKILLPORT_EMBEDDING_PROVIDER"] = "none"
        removals.update(
            {
                "SKILLPORT_EMBEDDING_BASE_URL",
                "SKILLPORT_EMBEDDING_MODEL",
                "SKILLPORT_EMBEDDING_API_KEY",
                "OPENAI_API_KEY",
                "OPENAI_EMBEDDING_MODEL",
            }
        )
    elif provider == "local":
        defaults = DEFAULTS["local"]
        updates["SKILLPORT_EMBEDDING_PROVIDER"] = "local"
        updates["SKILLPORT_EMBEDDING_BASE_URL"] = base_url or defaults["base_url"]
        updates["SKILLPORT_EMBEDDING_MODEL"] = model or defaults["model"]
        removals.add("SKILLPORT_EMBEDDING_API_KEY")
    elif provider == "openai":
        updates["SKILLPORT_EMBEDDING_PROVIDER"] = "openai"
        if model:
            updates["OPENAI_EMBEDDING_MODEL"] = model
        if api_key:
            updates["OPENAI_API_KEY"] = api_key
    elif provider == "dashscope":
        defaults = DEFAULTS["dashscope"]
        updates["SKILLPORT_EMBEDDING_PROVIDER"] = "dashscope"
        updates["SKILLPORT_EMBEDDING_BASE_URL"] = base_url or defaults["base_url"]
        updates["SKILLPORT_EMBEDDING_MODEL"] = model or defaults["model"]
        if api_key:
            updates["DASHSCOPE_API_KEY"] = api_key
    else:
        updates["SKILLPORT_EMBEDDING_PROVIDER"] = provider
        updates["SKILLPORT_EMBEDDING_BASE_URL"] = _require(base_url, "Base URL")
        updates["SKILLPORT_EMBEDDING_MODEL"] = _require(model, "Model")
        if api_key:
            updates["SKILLPORT_EMBEDDING_API_KEY"] = api_key

    env_file = env_file.expanduser().resolve()
    _update_env_file(env_file, updates, removals)
    console.print(f"[green]Updated[/green] {env_file}")
    console.print("[dim]Current values:[/dim]")
    for key in (
        "SKILLPORT_EMBEDDING_PROVIDER",
        "SKILLPORT_EMBEDDING_BASE_URL",
        "SKILLPORT_EMBEDDING_MODEL",
        "SKILLPORT_EMBEDDING_API_KEY",
        "DASHSCOPE_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_EMBEDDING_MODEL",
    ):
        if key in updates:
            console.print(f"[dim]{key}={updates[key]}[/dim]")
