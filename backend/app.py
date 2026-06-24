from __future__ import annotations

import json
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4
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
DEFAULT_PREVISTOS_PATH = BASE_DIR / "data" / "operacional" / "previstos_atrativos.json"
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
        "previstos_path": Path(os.getenv("EMPETUR_PREVISTOS_FILE", str(DEFAULT_PREVISTOS_PATH))),
        "supabase_url": normalize_supabase_url(os.getenv("SUPABASE_URL")),
        "supabase_service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip(),
        "supabase_schema": os.getenv("SUPABASE_SCHEMA", "public").strip() or "public",
        "supabase_table_status": os.getenv("SUPABASE_TABLE_STATUS", "empetur_municipios_status").strip()
        or "empetur_municipios_status",
        "supabase_table_base": os.getenv("SUPABASE_TABLE_BASE", "empetur_tabela_base").strip()
        or "empetur_tabela_base",
        "supabase_table_previstos": os.getenv("SUPABASE_TABLE_PREVISTOS", "empetur_previstos_atrativos").strip()
        or "empetur_previstos_atrativos",
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


class PrevistoRow(BaseModel):
    regiao: str = ""
    municipio: str = ""
    categoria: str = ""
    referencia: str = ""
    atrativo: str = ""


class PrevistoReplaceRequest(BaseModel):
    rows: list[PrevistoRow] = Field(default_factory=list)


def parse_generated_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


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


def build_supabase_previstos_url() -> str:
    settings = get_settings()
    return f"{settings['supabase_url']}/rest/v1/{settings['supabase_table_previstos']}"


def build_supabase_base_url() -> str:
    settings = get_settings()
    return f"{settings['supabase_url']}/rest/v1/{settings['supabase_table_base']}"


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


def has_supabase_previstos_backend() -> bool:
    return has_supabase_status_backend()


def has_supabase_base_backend() -> bool:
    return has_supabase_status_backend()


def normalize_base_row(row: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for field in BASE_FIELDNAMES:
        normalized[field] = str(row.get(field, "") or "").strip()
    return normalized


def validate_base_rows_for_supabase(rows: list[dict[str, Any]]) -> None:
    missing_identifiers = [
        row
        for row in rows
        if not str(row.get("codigo_pesquisa", "") or "").strip()
        or not str(row.get("nro_identificacao", "") or "").strip()
    ]
    if missing_identifiers:
        sample = missing_identifiers[0]
        raise HTTPException(
            status_code=422,
            detail=(
                "Nao foi possivel persistir a base consolidada no Supabase porque ha registros sem "
                "'codigo_pesquisa' ou 'nro_identificacao'. "
                f"Exemplo: questionario='{sample.get('questionario_preenchido', '')}', "
                f"municipio='{sample.get('municipio', '')}', atrativo='{sample.get('nome_atrativo', '')}'."
            ),
        )


def read_base_rows_from_supabase() -> list[dict[str, str]]:
    url = build_supabase_base_url()
    params = {
        "select": ",".join(BASE_FIELDNAMES),
        "order": "data_inicio_coleta.asc.nullslast,questionario_preenchido.asc,nro_identificacao.asc",
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.get(url, params=params, headers=build_supabase_headers())
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao ler base consolidada no Supabase: {exc.response.status_code}",
        ) from exc

    data = response.json()
    if not isinstance(data, list):
        return []
    return [normalize_base_row(item or {}) for item in data]


def replace_base_rows_for_form_supabase(codigo_pesquisa: int, rows: list[dict[str, Any]]) -> int:
    url = build_supabase_base_url()
    codigo = str(codigo_pesquisa)
    delete_params = {"codigo_pesquisa": f"eq.{codigo}"}
    with httpx.Client(timeout=60.0) as client:
        delete_response = client.delete(url, params=delete_params, headers=build_supabase_headers())
    try:
        delete_response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Falha ao limpar registros anteriores do questionario {codigo_pesquisa} "
                f"na base consolidada do Supabase: {exc.response.status_code}"
            ),
        ) from exc

    normalized_rows = [normalize_base_row(row) for row in rows]
    if not normalized_rows:
        return 0

    with httpx.Client(timeout=60.0) as client:
        insert_response = client.post(
            url,
            headers=build_supabase_headers(write=True),
            json=normalized_rows,
        )
    try:
        insert_response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Falha ao gravar registros do questionario {codigo_pesquisa} "
                f"na base consolidada do Supabase: {exc.response.status_code}"
            ),
        ) from exc

    return len(normalized_rows)


def persist_base_rows_to_supabase(rows: list[dict[str, Any]]) -> dict[str, int]:
    validate_base_rows_for_supabase(rows)
    rows_by_form: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        codigo = int(str(row.get("codigo_pesquisa", "")).strip())
        rows_by_form.setdefault(codigo, []).append(row)

    persisted_by_form: dict[str, int] = {}
    for codigo_pesquisa, form_rows in rows_by_form.items():
        persisted_by_form[str(codigo_pesquisa)] = replace_base_rows_for_form_supabase(codigo_pesquisa, form_rows)
    return persisted_by_form


def build_payload_from_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    generated_dt = max(
        (
            parsed
            for parsed in (
                parse_generated_timestamp(row.get("data_hora_execucao_carga", ""))
                for row in rows
            )
            if parsed is not None
        ),
        default=None,
    )
    if generated_dt is None:
        generated_dt = datetime.now(APP_TIMEZONE)
    exec_timestamp = generated_dt.strftime("%d/%m/%Y %H:%M:%S")
    exec_date = generated_dt.strftime("%d/%m/%Y")
    return build_dashboard_payload(rows, exec_date, exec_timestamp)


def normalize_previsto_row(municipio_slug: str, row: dict[str, Any]) -> dict[str, str]:
    return {
        "municipio_slug": municipio_slug,
        "regiao": str(row.get("regiao", "") or "").strip(),
        "municipio": str(row.get("municipio", "") or "").strip(),
        "categoria": str(row.get("categoria", "") or "").strip(),
        "referencia": str(row.get("referencia", "") or "").strip(),
        "atrativo": str(row.get("atrativo", "") or "").strip(),
    }


def read_previstos_local() -> dict[str, list[dict[str, str]]]:
    path = get_settings()["previstos_path"]
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Arquivo de previstos invalido: {exc}") from exc
    if not isinstance(raw, dict):
        return {}
    result: dict[str, list[dict[str, str]]] = {}
    for key, value in raw.items():
        if not isinstance(value, list):
            continue
        result[str(key)] = [normalize_previsto_row(str(key), item or {}) for item in value]
    return result


def write_previstos_local(data: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    path = get_settings()["previstos_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def read_previstos_by_municipio_local(municipio_slug: str) -> list[dict[str, str]]:
    return read_previstos_local().get(municipio_slug, [])


def read_previstos_summary_local() -> dict[str, Any]:
    data = read_previstos_local()
    by_municipio = {
        municipio_slug: len(rows)
        for municipio_slug, rows in data.items()
    }
    return {
        "total_previstos": sum(by_municipio.values()),
        "municipios": by_municipio,
    }


def replace_previstos_by_municipio_local(
    municipio_slug: str, rows: list[dict[str, Any]]
) -> list[dict[str, str]]:
    data = read_previstos_local()
    data[municipio_slug] = [normalize_previsto_row(municipio_slug, row) for row in rows]
    write_previstos_local(data)
    return data[municipio_slug]


def read_previstos_by_municipio_supabase(municipio_slug: str) -> list[dict[str, str]]:
    url = build_supabase_previstos_url()
    params = {
        "select": "municipio_slug,regiao,municipio,categoria,referencia,atrativo",
        "municipio_slug": f"eq.{municipio_slug}",
        "order": "categoria.asc,referencia.asc,atrativo.asc",
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, params=params, headers=build_supabase_headers())
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao ler previstos no Supabase: {exc.response.status_code}",
        ) from exc
    data = response.json()
    if not isinstance(data, list):
        return []
    return [normalize_previsto_row(municipio_slug, item or {}) for item in data]


def read_previstos_summary_supabase() -> dict[str, Any]:
    url = build_supabase_previstos_url()
    params = {
        "select": "municipio_slug",
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, params=params, headers=build_supabase_headers())
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao ler resumo de previstos no Supabase: {exc.response.status_code}",
        ) from exc
    data = response.json()
    if not isinstance(data, list):
        return {"total_previstos": 0, "municipios": {}}

    by_municipio: dict[str, int] = {}
    for item in data:
        municipio_slug = str((item or {}).get("municipio_slug", "")).strip()
        if not municipio_slug:
            continue
        by_municipio[municipio_slug] = by_municipio.get(municipio_slug, 0) + 1

    return {
        "total_previstos": sum(by_municipio.values()),
        "municipios": by_municipio,
    }


def replace_previstos_by_municipio_supabase(
    municipio_slug: str, rows: list[dict[str, Any]]
) -> list[dict[str, str]]:
    url = build_supabase_previstos_url()
    delete_params = {"municipio_slug": f"eq.{municipio_slug}"}
    with httpx.Client(timeout=30.0) as client:
        delete_response = client.delete(url, params=delete_params, headers=build_supabase_headers())
    try:
        delete_response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao limpar previstos no Supabase: {exc.response.status_code}",
        ) from exc

    normalized_rows = [normalize_previsto_row(municipio_slug, row) for row in rows]
    if normalized_rows:
        with httpx.Client(timeout=30.0) as client:
            insert_response = client.post(
                url,
                headers=build_supabase_headers(write=True),
                json=normalized_rows,
            )
        try:
            insert_response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Falha ao gravar previstos no Supabase: {exc.response.status_code}",
            ) from exc

    return read_previstos_by_municipio_supabase(municipio_slug)


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


@app.get("/api/previstos/{municipio_slug}")
def get_previstos_by_municipio(municipio_slug: str) -> dict[str, Any]:
    rows = (
        read_previstos_by_municipio_supabase(municipio_slug)
        if has_supabase_previstos_backend()
        else read_previstos_by_municipio_local(municipio_slug)
    )
    return {
        "municipio_slug": municipio_slug,
        "rows": rows,
        "total": len(rows),
    }


@app.get("/api/previstos-resumo")
def get_previstos_summary() -> dict[str, Any]:
    summary = (
        read_previstos_summary_supabase()
        if has_supabase_previstos_backend()
        else read_previstos_summary_local()
    )
    return summary


@app.put("/api/previstos/{municipio_slug}")
def replace_previstos_by_municipio(
    municipio_slug: str, request: PrevistoReplaceRequest
) -> dict[str, Any]:
    rows = [row.model_dump() for row in request.rows]
    saved_rows = (
        replace_previstos_by_municipio_supabase(municipio_slug, rows)
        if has_supabase_previstos_backend()
        else replace_previstos_by_municipio_local(municipio_slug, rows)
    )
    return {
        "status": "ok",
        "municipio_slug": municipio_slug,
        "rows": saved_rows,
        "total": len(saved_rows),
    }


@app.get("/api/dashboard/payload")
async def get_dashboard_payload() -> dict:
    settings = get_settings()
    payload_url = settings["payload_url"]
    payload_path = settings["payload_path"]

    if SYNC_CACHE.get("payload"):
        return SYNC_CACHE["payload"]

    if has_supabase_base_backend():
        supabase_rows = read_base_rows_from_supabase()
        if supabase_rows:
            payload = build_payload_from_rows(supabase_rows)
            SYNC_CACHE["payload"] = payload
            SYNC_CACHE["generated_at"] = payload.get("generated_at", "")
            return payload

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
    sync_run_id = str(uuid4())

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
            for row in rows:
                row["codigo_pesquisa"] = str(form.codigo_pesquisa)
                row["sync_run_id"] = sync_run_id
            all_rows.extend(rows)
            download_summary.append(
                {
                    "questionario": questionario,
                    "codigo_pesquisa": form.codigo_pesquisa,
                    "linhas_consolidadas": len(rows),
                }
            )

    persisted_supabase = False
    persisted_by_form: dict[str, int] = {}
    payload_rows = all_rows
    if has_supabase_base_backend():
        persisted_by_form = persist_base_rows_to_supabase(all_rows)
        persisted_supabase = True
        payload_rows = read_base_rows_from_supabase()

    payload = build_payload_from_rows(payload_rows)
    SYNC_CACHE["payload"] = payload
    SYNC_CACHE["generated_at"] = str(payload.get("generated_at", exec_timestamp))

    if request.persist_local:
        persist_sync_outputs(payload, payload_rows)

    return {
        "status": "ok",
        "generated_at": exec_timestamp,
        "sync_run_id": sync_run_id,
        "questionarios_processados": len(forms),
        "questionarios_ignorados": skipped_forms,
        "linhas_consolidadas": len(all_rows),
        "persistido_supabase": persisted_supabase,
        "linhas_persistidas_por_questionario": persisted_by_form,
        "downloads": download_summary,
    }
