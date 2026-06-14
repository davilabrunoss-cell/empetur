from __future__ import annotations

import json
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

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
APP_TIMEZONE = ZoneInfo("America/Sao_Paulo")
DEFAULT_PAYLOAD_PATH = BASE_DIR / "data" / "consolidado" / "dashboard_payload.json"
DEFAULT_BASE_CSV_PATH = BASE_DIR / "data" / "consolidado" / "empetur_tabela_base.csv"
DEFAULT_MUNICIPIOS_STATUS_PATH = BASE_DIR / "data" / "operacional" / "municipios_status.json"
DEFAULT_DISABLED_FORMS = {
    normalize_questionario_name("Sistema Marítimo e Fluvial"),
    normalize_questionario_name("Sistema Aéreo"),
    normalize_questionario_name("Sistemas de Comunicações"),
    normalize_questionario_name("Informações Turísticas"),
    normalize_questionario_name("Empresas Organizadoras de Eventos"),
    normalize_questionario_name("Folguedos, Crenças Populares"),
}


def parse_cors_origins(raw_value: str | None) -> list[str]:
    if not raw_value:
        return ["*"]
    origins = [item.strip() for item in raw_value.split(",") if item.strip()]
    return origins or ["*"]


def parse_disabled_forms(raw_value: str | None) -> set[str]:
    if not raw_value or not raw_value.strip():
        return set(DEFAULT_DISABLED_FORMS)
    return {
        normalize_questionario_name(item)
        for item in raw_value.split(",")
        if item.strip()
    }


def normalize_supabase_url(raw_value: str | None) -> str:
    if not raw_value:
        return ""
    return raw_value.rstrip("/")


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
        "municipios_status_path": Path(
            os.getenv("EMPETUR_MUNICIPIOS_STATUS_FILE", str(DEFAULT_MUNICIPIOS_STATUS_PATH))
        ),
        "supabase_url": normalize_supabase_url(os.getenv("SUPABASE_URL")),
        "supabase_service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip(),
        "supabase_schema": os.getenv("SUPABASE_SCHEMA", "public").strip() or "public",
        "supabase_table_status": os.getenv("SUPABASE_TABLE_STATUS", "empetur_municipios_status").strip()
        or "empetur_municipios_status",
        "cors_origins": parse_cors_origins(os.getenv("EMPETUR_CORS_ORIGINS")),
        "ipesquisa_base_url": os.getenv("IPESQUISA_BASE_URL", "https://sistema.ipesquisa.net").rstrip("/"),
        "ipesquisa_api_path": os.getenv("IPESQUISA_API_PATH", "/api/v1/pesquisa/{id}/get-csv-cases").strip(),
        "ipesquisa_client_id": os.getenv("IPESQUISA_CLIENT_ID", "").strip(),
        "ipesquisa_client_secret": os.getenv("IPESQUISA_CLIENT_SECRET", "").strip(),
        "ipesquisa_timeout_seconds": int(os.getenv("IPESQUISA_TIMEOUT_SECONDS", "60")),
        "ipesquisa_form_map": form_map,
        "ipesquisa_disabled_forms": parse_disabled_forms(os.getenv("IPESQUISA_DISABLED_FORMS")),
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
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
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


class MunicipioStatusUpdate(BaseModel):
    concluido: bool


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
    disabled_forms = get_settings()["ipesquisa_disabled_forms"]
    if request_forms:
        return [
            form
            for form in request_forms
            if normalize_questionario_name(form.questionario) not in disabled_forms
        ]

    form_map = get_settings()["ipesquisa_form_map"]
    if not form_map:
        return []

    return [
        SyncForm(questionario=questionario, codigo_pesquisa=codigo)
        for questionario, codigo in form_map.items()
        if normalize_questionario_name(questionario) not in disabled_forms
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


def read_municipios_status() -> dict[str, bool]:
    path = get_settings()["municipios_status_path"]
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Arquivo de status invalido: {exc}") from exc

    if not isinstance(raw, dict):
        return {}

    return {
        str(key): bool(value)
        for key, value in raw.items()
    }


def write_municipios_status(status_map: dict[str, bool]) -> dict[str, bool]:
    path = get_settings()["municipios_status_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        key: bool(value)
        for key, value in sorted(status_map.items())
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def has_supabase_status_backend() -> bool:
    settings = get_settings()
    return bool(settings["supabase_url"] and settings["supabase_service_role_key"])


def build_supabase_headers(write: bool = False) -> dict[str, str]:
    settings = get_settings()
    headers = {
        "apikey": str(settings["supabase_service_role_key"]),
        "Authorization": f"Bearer {settings['supabase_service_role_key']}",
        "Accept": "application/json",
        "Accept-Profile": str(settings["supabase_schema"]),
    }
    if write:
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        headers["Content-Profile"] = str(settings["supabase_schema"])
    return headers


def build_supabase_status_url() -> str:
    settings = get_settings()
    return f"{settings['supabase_url']}/rest/v1/{settings['supabase_table_status']}"


def read_municipios_status_from_supabase() -> dict[str, bool]:
    url = build_supabase_status_url()
    params = {"select": "municipio_slug,concluido"}
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, params=params, headers=build_supabase_headers())
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao ler status de municipios no Supabase: {exc.response.status_code}",
        ) from exc

    data = response.json()
    if not isinstance(data, list):
        return {}

    return {
        str(item.get("municipio_slug", "")): bool(item.get("concluido"))
        for item in data
        if item.get("municipio_slug")
    }


def write_municipio_status_to_supabase(municipio_slug: str, concluido: bool) -> dict[str, bool]:
    url = build_supabase_status_url()
    payload = [{"municipio_slug": municipio_slug, "concluido": concluido}]
    params = {"on_conflict": "municipio_slug"}
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, params=params, headers=build_supabase_headers(write=True), json=payload)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao gravar status de municipios no Supabase: {exc.response.status_code}",
        ) from exc

    return read_municipios_status_from_supabase()


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/municipios/status")
def get_municipios_status() -> dict[str, dict[str, bool]]:
    if has_supabase_status_backend():
        return {"concluded": read_municipios_status_from_supabase()}
    return {"concluded": read_municipios_status()}


@app.put("/api/municipios/status/{municipio_slug}")
def update_municipio_status(municipio_slug: str, request: MunicipioStatusUpdate) -> dict[str, Any]:
    if has_supabase_status_backend():
        saved = write_municipio_status_to_supabase(municipio_slug, request.concluido)
    else:
        status_map = read_municipios_status()
        status_map[municipio_slug] = request.concluido
        saved = write_municipios_status(status_map)
    return {
        "status": "ok",
        "municipio_slug": municipio_slug,
        "concluido": request.concluido,
        "concluded": saved,
    }


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
    disabled_forms = settings["ipesquisa_disabled_forms"]
    skipped_forms = sorted(disabled_forms)
    if request.forms:
        skipped_forms = sorted(
            {
                normalize_questionario_name(form.questionario)
                for form in request.forms
                if normalize_questionario_name(form.questionario) in disabled_forms
            }
        )
    forms = build_sync_forms(request.forms)

    if not auth:
        raise HTTPException(
            status_code=503,
            detail="Configure IPESQUISA_CLIENT_ID e IPESQUISA_CLIENT_SECRET no ambiente do Render.",
        )
    if not forms:
        raise HTTPException(
            status_code=400,
            detail=(
                "Nenhum questionario apto para sincronizacao. "
                "Envie forms na requisicao, configure IPESQUISA_FORM_MAP "
                "ou revise IPESQUISA_DISABLED_FORMS."
            ),
        )

    exec_now = datetime.now(APP_TIMEZONE)
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
                    detail=f"Falha ao consolidar o questionario '{questionario}': {exc}",
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
        "questionarios_ignorados": skipped_forms,
        "linhas_consolidadas": len(all_rows),
        "downloads": download_summary,
    }
