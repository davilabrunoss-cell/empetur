from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PAYLOAD_PATH = BASE_DIR / "data" / "consolidado" / "dashboard_payload.json"


def parse_cors_origins(raw_value: str | None) -> list[str]:
    if not raw_value:
        return ["*"]
    origins = [item.strip() for item in raw_value.split(",") if item.strip()]
    return origins or ["*"]


@lru_cache
def get_settings() -> dict[str, object]:
    payload_path = os.getenv("EMPETUR_PAYLOAD_FILE", str(DEFAULT_PAYLOAD_PATH))
    payload_url = os.getenv("EMPETUR_PAYLOAD_URL", "").strip()
    return {
        "payload_path": Path(payload_path),
        "payload_url": payload_url,
        "cors_origins": parse_cors_origins(os.getenv("EMPETUR_CORS_ORIGINS")),
    }


app = FastAPI(
    title="EMPETUR Dashboard API",
    version="0.1.0",
    description="API inicial para publicar o payload consolidado do dashboard EMPETUR.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings()["cors_origins"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def read_payload_from_disk(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de payload nao encontrado em: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


async def read_payload_from_url(url: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard/payload")
async def get_dashboard_payload() -> dict:
    settings = get_settings()
    payload_url = settings["payload_url"]
    payload_path = settings["payload_path"]

    if payload_url:
        try:
            return await read_payload_from_url(str(payload_url))
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Falha ao buscar payload remoto: {exc}") from exc

    try:
        return read_payload_from_disk(payload_path)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Payload do dashboard indisponivel. Configure EMPETUR_PAYLOAD_FILE "
                "ou EMPETUR_PAYLOAD_URL antes de publicar o frontend."
            ),
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Payload invalido: {exc}") from exc


@app.post("/api/sync/ipesquisa")
def sync_ipesquisa_placeholder() -> dict[str, str]:
    return {
        "status": "pending",
        "message": (
            "Endpoint reservado para a sincronizacao com a API do iPesquisa. "
            "A implementacao completa sera conectada ao Supabase na proxima etapa."
        ),
    }
