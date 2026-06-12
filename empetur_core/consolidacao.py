from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
REFERENCE_DIR = BASE_DIR / "data" / "referencias"

FILE_PREFIX = "#1265803711 _ EMPETUR - "
BASE_FIELDNAMES = [
    "arquivo_origem",
    "questionario_preenchido",
    "municipio",
    "categoria",
    "nome_atrativo",
    "pesquisador_informado",
    "pesquisador_sistema",
    "pesquisador",
    "data_inicio_coleta",
    "data_fim_coleta",
    "linha_origem",
    "data_execucao_carga",
    "data_hora_execucao_carga",
]
TEST_NAME_PATTERNS = [
    re.compile(r"^\s*9{2,}\s*$"),
    re.compile(r"^\s*x{2,}\s*$", re.IGNORECASE),
    re.compile(r"\bteste(?:s|ndo|ando)?\b", re.IGNORECASE),
    re.compile(r"\btestar\b", re.IGNORECASE),
]


@dataclass(frozen=True)
class FileRule:
    questionario: str
    categoria_header_startswith: str | None
    nome_header_startswith: str


RULES_BY_QUESTIONARIO: dict[str, FileRule] = {
    "Agenciamento": FileRule("Agenciamento", "1. Tipo da Categoria", "3. Nome / Entidade"),
    "Alimentação": FileRule("Alimentação", "1. Tipo da Categoria", "3. Nome."),
    "Artesanato, Folclore, Gastronomia": FileRule(
        "Artesanato, Folclore, Gastronomia", "1. Tipo da Categoria", "3. Nome do Atrativo"
    ),
    "Artesanato-Detalhamento": FileRule("Artesanato-Detalhamento", "1. Tipo da Categoria", "3. Nome do Atrativo"),
    "Artesãos, Artistas Plásticos": FileRule(
        "Artesãos, Artistas Plásticos", "1. Tipo da Categoria", "3. Nome do Atrativo"
    ),
    "Atrativos Culturais": FileRule("Atrativos Culturais", "1. Tipo da Categoria", "3. Nome do Atrativo"),
    "Atrativos Naturais": FileRule("Atrativos Naturais", "1. Tipo da Categoria", "3. Nome do Atrativo"),
    "Compras": FileRule("Compras", "1. Tipo da Categoria", "3. Nome / Entidade"),
    "Entretenimento": FileRule("Entretenimento", "1. Tipo da Categoria", "3. Nome."),
    "Feiras e Exposições": FileRule("Feiras e Exposições", "1. Tipo da Categoria", "3. Nome do Atrativo"),
    "Feiras Livres, Mercados Públicos": FileRule(
        "Feiras Livres, Mercados Públicos", "1. Tipo da Categoria", "3. Nome do Atrativo"
    ),
    "Festas Populares e Religiosas": FileRule(
        "Festas Populares e Religiosas", "1. Tipo da Categoria", "3. Nome do Atrativo"
    ),
    "Folclore-Detalhado": FileRule("Folclore-Detalhado", "1. Tipo da Categoria", "3. Nome do Atrativo"),
    "Gastronomia-Detalhado": FileRule("Gastronomia-Detalhado", "1. Tipo da Categoria", "3. Nome do Atrativo"),
    "Hospedagens": FileRule("Hospedagens", "1. Tipo da Categoria", "3. Nome."),
    "Instalações Desportivas": FileRule("Instalações Desportivas", "1. Tipo da Categoria", "3. Nome."),
    "Locais de Convernções, Exposições e Eventos Sociais": FileRule(
        "Locais de Convernções, Exposições e Eventos Sociais", "1. Tipo da Categoria", "3. Nome."
    ),
    "Outros Servicos de Apoio Turistico": FileRule(
        "Outros Servicos de Apoio Turistico", "1. Tipo da Categoria", "3. Nome / Entidade"
    ),
    "Roteiros Turísticos": FileRule("Roteiros Turísticos", "1. Tipo da Categoria", "2. Nome do roteiro turístico"),
    "Sistema de Segurança": FileRule("Sistema de Segurança", "1. Tipo da Categoria", "3. Nome / Entidade"),
    "Sistema Médico-Hospitalar": FileRule(
        "Sistema Médico-Hospitalar", "1. Tipo da Categoria", "2. Nome / Entidade"
    ),
    "Sistema Rodoviário": FileRule("Sistema Rodoviário", None, "2. Nome."),
    "Transportes Turisticos": FileRule("Transportes Turisticos", "1. Tipo da Categoria", "3. Nome / Entidade"),
}


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def normalize_for_match(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    without_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return without_accents.strip().lower()


def fix_mojibake(value: str) -> str:
    if not value:
        return value
    if "Ã" not in value and "Â" not in value:
        return value
    try:
        return value.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return value


def normalize_questionario_name(value: str) -> str:
    return fix_mojibake(normalize_text(value))


def get_rule_for_questionario(questionario: str) -> FileRule:
    normalized = normalize_for_match(questionario)
    for candidate, rule in RULES_BY_QUESTIONARIO.items():
        if normalize_for_match(candidate) == normalized:
            return rule
    raise KeyError(f"Questionario sem regra de normalizacao: {questionario}")


def extract_questionario(file_name: str) -> str:
    if not file_name.startswith(FILE_PREFIX):
        raise ValueError(f"Arquivo fora do padrao esperado: {file_name}")
    remainder = file_name[len(FILE_PREFIX) :]
    if remainder.lower().endswith(".csv"):
        remainder = remainder[:-4]
    questionario = re.sub(r"\s*-\s*NOVO$", "", remainder, flags=re.IGNORECASE)
    questionario = re.sub(r"\s*-\s*\d{4}(?:\s*-\s*Para Revisar)?$", "", questionario, flags=re.IGNORECASE)
    questionario = normalize_questionario_name(questionario)
    if not questionario:
        raise ValueError(f"Nao foi possivel extrair o questionario de: {file_name}")
    return questionario


def is_test_record_name(value: str) -> bool:
    normalized = normalize_for_match(fix_mojibake(value))
    if not normalized:
        return False
    return any(pattern.search(normalized) for pattern in TEST_NAME_PATTERNS)


def find_index(header: list[str], predicate) -> int:
    for idx, column in enumerate(header):
        if predicate(column):
            return idx
    raise KeyError("Coluna esperada nao encontrada")


def find_optional_index(header: list[str], predicate) -> int | None:
    for idx, column in enumerate(header):
        if predicate(column):
            return idx
    return None


def get_value(row: list[str], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    return fix_mojibake(normalize_text(row[idx]))


def parse_br_datetime(value: str) -> datetime | None:
    value = normalize_text(value)
    if not value:
        return None
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def decode_csv_bytes(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def parse_csv_text(content: str) -> list[list[str]]:
    return list(csv.reader(content.splitlines()))


def consolidate_csv_rows(file_name: str, rows: list[list[str]], exec_date: str, exec_timestamp: str) -> list[dict[str, str]]:
    questionario = extract_questionario(file_name)
    rule = get_rule_for_questionario(questionario)

    header = [fix_mojibake(item) for item in rows[0]]
    data_rows = rows[1:]

    municipio_idx = find_index(header, lambda c: c.startswith("P0. Munic"))
    nome_idx = find_index(header, lambda c: c.startswith(rule.nome_header_startswith))
    pesquisador_informado_idx = find_optional_index(
        header,
        lambda c: "Pesquisador:" in c and normalize_text(c) != "Pesquisador",
    )
    pesquisador_sistema_idx = find_optional_index(header, lambda c: normalize_text(c) == "Pesquisador")
    data_inicio_idx = find_optional_index(header, lambda c: normalize_text(c).startswith("Data In"))
    data_fim_idx = find_optional_index(header, lambda c: normalize_text(c) == "Data Fim")

    categoria_idx = None
    if rule.categoria_header_startswith is not None:
        categoria_idx = find_index(header, lambda c: c.startswith(rule.categoria_header_startswith))

    consolidated_rows: list[dict[str, str]] = []
    for row_number, row in enumerate(data_rows, start=2):
        nome_atrativo = get_value(row, nome_idx)
        if is_test_record_name(nome_atrativo):
            continue

        pesquisador_informado = get_value(row, pesquisador_informado_idx)
        pesquisador_sistema = get_value(row, pesquisador_sistema_idx)
        categoria = questionario if questionario == "Sistema Rodoviário" else get_value(row, categoria_idx)

        consolidated_rows.append(
            {
                "arquivo_origem": file_name,
                "questionario_preenchido": questionario,
                "municipio": get_value(row, municipio_idx),
                "categoria": categoria,
                "nome_atrativo": nome_atrativo,
                "pesquisador_informado": pesquisador_informado,
                "pesquisador_sistema": pesquisador_sistema,
                "pesquisador": pesquisador_informado or pesquisador_sistema,
                "data_inicio_coleta": get_value(row, data_inicio_idx),
                "data_fim_coleta": get_value(row, data_fim_idx),
                "linha_origem": str(row_number),
                "data_execucao_carga": exec_date,
                "data_hora_execucao_carga": exec_timestamp,
            }
        )

    return consolidated_rows


def consolidate_csv_content(file_name: str, content: bytes | str, exec_date: str, exec_timestamp: str) -> list[dict[str, str]]:
    text = content if isinstance(content, str) else decode_csv_bytes(content)
    rows = parse_csv_text(text)
    if not rows:
        return []
    return consolidate_csv_rows(file_name, rows, exec_date, exec_timestamp)


def consolidate_csv_file(path: Path, exec_date: str, exec_timestamp: str) -> list[dict[str, str]]:
    return consolidate_csv_content(path.name, path.read_bytes(), exec_date, exec_timestamp)


def load_cadastro_municipios() -> list[dict[str, str]]:
    path = REFERENCE_DIR / "cadastro_municipios.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_total_previsto() -> dict[str, int]:
    path = REFERENCE_DIR / "total_previsto_municipios.csv"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out: dict[str, int] = {}
    for row in rows:
        raw = normalize_text(row.get("total_previsto", ""))
        if raw == "":
            out[row["municipio"]] = 0
            continue
        try:
            out[row["municipio"]] = int(float(raw.replace(",", ".")))
        except ValueError:
            out[row["municipio"]] = 0
    return out


def build_resumos(all_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    cadastro = load_cadastro_municipios()
    previstos = load_total_previsto()

    rows_by_municipio: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in all_rows:
        rows_by_municipio[row["municipio"]].append(row)

    resumo_municipios: list[dict[str, str]] = []
    for item in cadastro:
        municipio = item["municipio"]
        municipio_rows = rows_by_municipio.get(municipio, [])
        total_realizado = len(municipio_rows)
        total_previsto = previstos.get(municipio, 0)
        faltante = max(total_previsto - total_realizado, 0)
        percentual = round((total_realizado / total_previsto) * 100, 2) if total_previsto > 0 else 0

        datas_inicio = [parse_br_datetime(r["data_inicio_coleta"]) for r in municipio_rows]
        datas_inicio = [d for d in datas_inicio if d is not None]

        primeira = min(datas_inicio).strftime("%d/%m/%Y %H:%M:%S") if datas_inicio else ""
        ultima = max(datas_inicio).strftime("%d/%m/%Y %H:%M:%S") if datas_inicio else ""

        resumo_municipios.append(
            {
                "regiao": item["regiao"],
                "ordem_regiao": item["ordem_regiao"],
                "municipio": municipio,
                "ordem_municipio": item["ordem_municipio"],
                "total_realizado": str(total_realizado),
                "total_previsto": str(total_previsto),
                "faltante": str(faltante),
                "percentual_cobertura": f"{percentual:.2f}",
                "primeira_coleta": primeira,
                "ultima_coleta": ultima,
            }
        )

    resumo_questionarios_counter = Counter(row["questionario_preenchido"] for row in all_rows)
    resumo_questionarios = [
        {"questionario_preenchido": nome, "total": str(total)}
        for nome, total in sorted(resumo_questionarios_counter.items(), key=lambda item: (-item[1], item[0]))
    ]

    resumo_pesquisadores_counter = Counter(row["pesquisador"] for row in all_rows if normalize_text(row["pesquisador"]))
    resumo_pesquisadores = [
        {"pesquisador": nome, "total": str(total)}
        for nome, total in sorted(resumo_pesquisadores_counter.items(), key=lambda item: (-item[1], item[0]))
    ]

    resumo_municipio_categoria_counter = Counter((row["municipio"], row["categoria"]) for row in all_rows)
    resumo_municipio_categoria = [
        {"municipio": municipio, "categoria": categoria, "total": str(total)}
        for (municipio, categoria), total in sorted(
            resumo_municipio_categoria_counter.items(), key=lambda item: (item[0][0], item[0][1])
        )
    ]

    return {
        "cadastro_municipios": cadastro,
        "resumo_municipios": resumo_municipios,
        "resumo_questionarios": resumo_questionarios,
        "resumo_pesquisadores": resumo_pesquisadores,
        "resumo_municipio_categoria": resumo_municipio_categoria,
    }


def build_dashboard_payload(all_rows: list[dict[str, str]], exec_date: str, exec_timestamp: str) -> dict:
    return {
        "generated_at": exec_timestamp,
        "generated_date": exec_date,
        "base_rows": all_rows,
        **build_resumos(all_rows),
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
