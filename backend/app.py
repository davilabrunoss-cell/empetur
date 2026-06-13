from __future__ import annotations

import json
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from empetur_core.consolidacao import (
    BASE_FIELDNAMES,
    FILE_PREFIX,
    build_dashboard_payload,
    consolidate_csv_content,
    normalize_questionario_name,
    write_csv,
    write_json,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PAYLOAD_PATH = BASE_DIR / "data" / "consolidado" / "dashboard_payload.json"
DEFAULT_BASE_CSV_PATH = BASE_DIR / "data" / "consolidado" / "empetur_tabela_base.csv"


def parse_cors_origins(raw_value: str | None) -> list[str]:
    if not raw_value:
        return ["*"]
    origins = [item.strip() for item in raw_value.split(",") if item.strip()]
    return origins or ["*"]


@lru_cache
def get_settings() -> dict[str, object]:
    payload_path = os.getenv("EMPETUR_PAYLOAD_FILE", str(DEFAULT_PAYLOAD_PATH))
    payload_url = os.getenv("EMPETUR_PAYLOAD_URL", "").strip()
    form_map_raw = os.getenv("IPESQUISA_FORM_MAP", "").strip()
    form_map: dict[str, int] = {}
    if form_map_raw:
        try:
            parsed = json.loads(form_map_raw)
            if isinstance(parsed, dict):
                form_map = {normalize_questionario_name(str(key)): int(value) for key, value in parsed.items()}
        except (ValueError, TypeError):
            form_map = {}
    return {
        "payload_path": Path(payload_path),
        "payload_url": payload_url,
        "base_csv_path": Path(os.getenv("EMPETUR_BASE_CSV_FILE", str(DEFAULT_BASE_CSV_PATH))),
        "cors_origins": parse_cors_origins(os.getenv("EMPETUR_CORS_ORIGINS")),
        "ipesquisa_base_url": os.getenv("IPESQUISA_BASE_URL", "https://sistema.ipesquisa.net").rstrip("/"),
        "ipesquisa_api_path": os.getenv("IPESQUISA_API_PATH", "/api/v1/pesquisa/{id}/get-csv-cases").strip(),
        "ipesquisa_client_id": os.getenv("IPESQUISA_CLIENT_ID", "").strip(),
        "ipesquisa_client_secret": os.getenv("IPESQUISA_CLIENT_SECRET", "").strip(),
        "ipesquisa_timeout_seconds": int(os.getenv("IPESQUISA_TIMEOUT_SECONDS", "60")),
        "ipesquisa_form_map": form_map,
    }


app = FastAPI(
    title="EMPETUR Dashboard API",
    version="0.2.0",
    description="API do dashboard EMPETUR com sincronizacao manual a partir do iPesquisa.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings()["cors_origins"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

SYNC_CACHE: dict[str, Any] = {}


class SyncForm(BaseModel):
    questionario: str
    codigo_pesquisa: int = Field(..., gt=0)


class SyncRequest(BaseModel):
    forms: list[SyncForm] = Field(default_factory=list)
    dt_gravacao_inicio: str | None = None
    dt_gravacao_fim: str | None = None
    persist_local: bool = True


def read_payload_from_disk(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de payload nao encontrado em: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


async def read_payload_from_url(url: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def build_auth() -> httpx.BasicAuth | None:
    settings = get_settings()
    client_id = str(settings["ipesquisa_client_id"])
    client_secret = str(settings["ipesquisa_client_secret"])
    if client_id and client_secret:
        return httpx.BasicAuth(client_id, client_secret)
    return None


def build_sync_forms(request_forms: list[SyncForm]) -> list[SyncForm]:
    if request_forms:
        return request_forms

    form_map = get_settings()["ipesquisa_form_map"]
    if not form_map:
        return []

    return [
        SyncForm(questionario=questionario, codigo_pesquisa=codigo)
        for questionario, codigo in form_map.items()
    ]


def build_csv_file_name(questionario: str) -> str:
    return f"{FILE_PREFIX}{questionario} - 2026.csv"


async def fetch_ipesquisa_csv(
    client: httpx.AsyncClient,
    questionario: str,
    codigo_pesquisa: int,
    dt_gravacao_inicio: str | None,
    dt_gravacao_fim: str | None,
) -> bytes:
    settings = get_settings()
    api_path = str(settings["ipesquisa_api_path"]).replace("{id}", str(codigo_pesquisa))
    url = f"{settings['ipesquisa_base_url']}{api_path}"
    params = {}
    if dt_gravacao_inicio:
        params["dt_gravacao_inicio"] = dt_gravacao_inicio
    if dt_gravacao_fim:
        params["dt_gravacao_fim"] = dt_gravacao_fim

    response = await client.get(url, params=params or None, headers={"Accept": "text/plain"})
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao baixar o CSV de {questionario} ({codigo_pesquisa}): {exc.response.status_code}",
        ) from exc
    return response.content


def persist_sync_outputs(payload: dict, all_rows: list[dict[str, str]]) -> None:
    settings = get_settings()
    write_json(settings["payload_path"], payload)
    write_csv(settings["base_csv_path"], BASE_FIELDNAMES, all_rows)


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard/payload")
async def get_dashboard_payload() -> dict:
    settings = get_settings()
    payload_url = settings["payload_url"]
    payload_path = settings["payload_path"]

    if SYNC_CACHE.get("payload"):
        return SYNC_CACHE["payload"]

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
                "Payload do dashboard indisponivel. Rode uma sincronizacao do iPesquisa "
                "ou configure EMPETUR_PAYLOAD_URL."
            ),
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Payload invalido: {exc}") from exc


@app.post("/api/sync/ipesquisa")
async def sync_ipesquisa(request: SyncRequest) -> dict[str, Any]:
    settings = get_settings()
    auth = build_auth()
    forms = build_sync_forms(request.forms)

    if not auth:
        raise HTTPException(
            status_code=503,
            detail="Configure IPESQUISA_CLIENT_ID e IPESQUISA_CLIENT_SECRET no ambiente do Render.",
        )
    if not forms:
        raise HTTPException(
            status_code=400,
            detail="Nenhum questionario informado. Envie forms na requisicao ou configure IPESQUISA_FORM_MAP.",
        )

    exec_now = datetime.now()
    exec_date = exec_now.strftime("%d/%m/%Y")
    exec_timestamp = exec_now.strftime("%d/%m/%Y %H:%M:%S")

    timeout = httpx.Timeout(float(settings["ipesquisa_timeout_seconds"]))
    all_rows: list[dict[str, str]] = []
    download_summary: list[dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=timeout, auth=auth) as client:
        for form in forms:
            questionario = normalize_questionario_name(form.questionario)
            csv_bytes = await fetch_ipesquisa_csv(
                client,
                questionario,
                form.codigo_pesquisa,
                request.dt_gravacao_inicio,
                request.dt_gravacao_fim,
            )
            try:
                rows = consolidate_csv_content(
                    build_csv_file_name(questionario),
                    csv_bytes,
                    exec_date,
                    exec_timestamp,
                )
            except KeyError as exc:
                raise HTTPException(
                    status_code=422,
                    detail=f"Falha ao consolidar o questionário '{questionario}': {exc}",
                ) from exc
            all_rows.extend(rows)
            download_summary.append(
                {
                    "questionario": questionario,
                    "codigo_pesquisa": form.codigo_pesquisa,
                    "linhas_consolidadas": len(rows),
                }
            )

    payload = build_dashboard_payload(all_rows, exec_date, exec_timestamp)
    SYNC_CACHE["payload"] = payload
    SYNC_CACHE["generated_at"] = exec_timestamp

    if request.persist_local:
        persist_sync_outputs(payload, all_rows)

    return {
        "status": "ok",
        "generated_at": exec_timestamp,
        "questionarios_processados": len(forms),
        "linhas_consolidadas": len(all_rows),
        "downloads": download_summary,
    }
