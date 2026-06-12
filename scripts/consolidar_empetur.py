from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from empetur_core.consolidacao import (
    BASE_FIELDNAMES,
    build_dashboard_payload,
    build_resumos,
    consolidate_csv_file,
    write_csv,
    write_json,
)

INPUT_DIR = BASE_DIR / "data" / "raw" / "empetur_bancos"
OUTPUT_DIR = BASE_DIR / "data" / "consolidado"
WEB_DATA_DIR = BASE_DIR / "web" / "public" / "data"


def main() -> None:
    exec_now = datetime.now()
    exec_date = exec_now.strftime("%d/%m/%Y")
    exec_timestamp = exec_now.strftime("%d/%m/%Y %H:%M:%S")

    all_rows: list[dict[str, str]] = []
    csv_files = sorted(INPUT_DIR.glob("*.csv"))
    for path in csv_files:
        all_rows.extend(consolidate_csv_file(path, exec_date, exec_timestamp))

    write_csv(OUTPUT_DIR / "empetur_tabela_base.csv", BASE_FIELDNAMES, all_rows)

    resumos = build_resumos(all_rows)
    write_csv(
        OUTPUT_DIR / "resumo_municipios.csv",
        [
            "regiao",
            "ordem_regiao",
            "municipio",
            "ordem_municipio",
            "total_realizado",
            "total_previsto",
            "faltante",
            "percentual_cobertura",
            "primeira_coleta",
            "ultima_coleta",
        ],
        resumos["resumo_municipios"],
    )
    write_csv(
        OUTPUT_DIR / "resumo_questionarios.csv",
        ["questionario_preenchido", "total"],
        resumos["resumo_questionarios"],
    )
    write_csv(
        OUTPUT_DIR / "resumo_pesquisadores.csv",
        ["pesquisador", "total"],
        resumos["resumo_pesquisadores"],
    )
    write_csv(
        OUTPUT_DIR / "resumo_municipio_categoria.csv",
        ["municipio", "categoria", "total"],
        resumos["resumo_municipio_categoria"],
    )

    dashboard_payload = build_dashboard_payload(all_rows, exec_date, exec_timestamp)
    write_json(OUTPUT_DIR / "dashboard_payload.json", dashboard_payload)
    write_json(WEB_DATA_DIR / "dashboard_payload.json", dashboard_payload)

    print(f"Arquivos lidos: {len(csv_files)}")
    print(f"Linhas consolidadas: {len(all_rows)}")
    print(f"Saida base: {OUTPUT_DIR / 'empetur_tabela_base.csv'}")


if __name__ == "__main__":
    main()
