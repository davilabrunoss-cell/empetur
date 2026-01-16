# ============================================================
# EMPETUR | Validação de Gabinete + Gestão de Campo (Streamlit)
# Bruno + Luna — v18 (layout ajustado - micro ajustes finais)
#  - Município alinhado com Busca global
#  - Botões de página abaixo do "Tudo salvo"
#  - Fonte dos botões em grafite
#  - Menos espaço entre filtros e tabela
#  - Categorias (gráfico) com fonte em grafite
# ============================================================

import os
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path  # <- deixa aqui em cima

import pandas as pd
import streamlit as st
import plotly.express as px

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

APP_TITLE = "Consolidação PRT"
APP_SUBTITLE = "Template Soberano Regional | EMPETUR / INVTUR"

# Caminho base do repositório (Streamlit Cloud / local)
BASE_DIR = Path(_file_).resolve().parent

# Arquivo na raiz do repo (mesmo nível do app.py)
DATA_FILE = str(BASE_DIR / "inventario_preliminar_app.xlsx")

# Colunas canônicas internas (app trabalha sempre com esses nomes)
CANONICAL_COLUMNS = [
    "municipio_id",
    "municipio_nome",
    "item_id",
    "status",
    "categoria",
    "nome",
    "endereco",
    "telefone",
    "email",
    "site",
    "latitude",
    "longitude",
    "descricao",
    "validacao_preliminar",
    "obs_preliminar",
    "enviar_campo",
    "visitado",
    "obs_campo",
]

VALIDATION_OPTIONS = ["Em branco", "Sim", "Pendente", "Não"]
STATUS_OPTIONS = ["Inventariado INVTUR", "Novo"]
ROUTE_BY_VALIDATION = {"Sim", "Pendente"}

# ------------------------------------------------------------
# CSS / UI
# ------------------------------------------------------------

def inject_css():
    st.markdown(
        """
        <style>
          :root{
            --navy:#002B5B;
            --emerald:#10B981;
            --amber:#F59E0B;
            --rose:#F43F5E;
            --slate:#0f172a;
            --slate2:#334155;
            --card:#ffffff;
            --border:#e2e8f0;
            --bg:#f8fafc;
          }

          .stApp{ background: var(--bg); }

          .topbar{
            background: var(--navy);
            color: white;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: .25em;
            text-transform: uppercase;
            padding: 10px 18px;
            border-bottom: 1px solid rgba(255,255,255,.08);
            display:flex;
            gap:12px;
            align-items:center;
            justify-content:center;
          }
          .dot{ width:4px; height:4px; background: rgba(255,255,255,.35); border-radius:999px; }

          .hero{
            background: white;
            border:1px solid var(--border);
            border-radius: 18px;
            padding: 18px 18px;
            box-shadow: 0 1px 0 rgba(0,0,0,.02);
          }
          .hero-title{
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .08em;
            color: var(--slate);
            margin: 0;
            font-size: 18px;
          }
          .hero-sub{
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .22em;
            color: #94a3b8;
            margin: 6px 0 0 0;
            font-size: 10px;
          }

          .kpi-grid{ display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 14px; }
          @media (max-width: 1100px){ .kpi-grid{ grid-template-columns: repeat(2, minmax(0,1fr)); } }
          @media (max-width: 650px){ .kpi-grid{ grid-template-columns: repeat(1, minmax(0,1fr)); } }

          .kpi{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 14px 14px; }
          .kpi-label{ font-size:10px; font-weight: 900; text-transform: uppercase; letter-spacing: .18em; color: #94a3b8; }
          .kpi-value{ font-size: 28px; font-weight: 900; color: var(--slate); line-height: 1.1; margin-top: 4px; }
          .kpi-foot{ margin-top: 8px; font-size:10px; font-weight: 900; text-transform: uppercase; letter-spacing: .18em; color: #64748b; }
          .bar-emerald{ border-bottom: 4px solid var(--emerald); }
          .bar-amber{ border-bottom: 4px solid var(--amber); }
          .bar-rose{ border-bottom: 4px solid var(--rose); }
          .bar-slate{ border-bottom: 4px solid var(--slate); }

          /* FIX DEFINITIVO — LABELS DOS FILTROS */
          label[data-testid="stWidgetLabel"],
          label[data-testid="stWidgetLabel"] *{
            color: var(--slate2) !important;
            opacity: 1 !important;
            font-weight: 800 !important;
          }
          div[data-testid="stWidgetLabel"],
          div[data-testid="stWidgetLabel"] *{
            color: var(--slate2) !important;
            opacity: 1 !important;
            font-weight: 800 !important;
          }
          div.stTextInput label,
          div.stSelectbox label,
          div.stMultiSelect label{
            color: var(--slate2) !important;
            opacity: 1 !important;
            font-weight: 800 !important;
          }
          div[data-testid="stCheckbox"] *,
          div[data-testid="stToggle"] *{
            color: var(--slate2) !important;
            opacity: 1 !important;
            font-weight: 700 !important;
          }

          /* Pill de status */
          .status-pill{
            display:flex;
            align-items:center;
            justify-content:center;
            gap:10px;
            border:1px solid var(--border);
            border-radius: 14px;
            padding: 10px 12px;
            background: white;
            height: 100%;
          }
          .status-dot{
            width:10px; height:10px; border-radius:999px;
          }
          .status-text{
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .14em;
            font-size: 10px;
            color: var(--slate);
          }

          /* ===== AJUSTE PEDIDO: fonte dos botões (radio) em grafite ===== */
          div[role="radiogroup"] label span{
            color: var(--slate2) !important;
            font-weight: 800 !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_topbar():
    st.markdown(
        f"""
        <div class="topbar">
          <span style="opacity:.55;">Auditoria Regional Soberana</span>
          <span class="dot"></span>
          <span>{APP_SUBTITLE}</span>
          <span class="dot"></span>
          <span style="color:var(--emerald);">Dados Reais</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_hero(muni_name: str, page_name: str):
    st.markdown(
        f"""
        <div class="hero">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
            <div>
              <p class="hero-title">{APP_TITLE} | Validação Técnica & Campo</p>
              <p class="hero-sub">{page_name} • {muni_name} • Localhost</p>
            </div>
            <div style="background: rgba(0,43,91,.08); border-radius:14px; padding:10px 12px;">
              <span style="font-weight:900; text-transform:uppercase; letter-spacing:.18em; color:#002B5B; font-size:10px;">
                Validação de Dados
              </span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_status_pill(dirty: bool):
    if dirty:
        color = "#F59E0B"
        txt = "Alterações pendentes"
    else:
        color = "#10B981"
        txt = "Tudo salvo"
    st.markdown(
        f"""
        <div class="status-pill">
          <div class="status-dot" style="background:{color};"></div>
          <div class="status-text">{txt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# DATA UTILS
# ------------------------------------------------------------

def safe_mkdir(path: str):
    os.makedirs(path, exist_ok=True)

def list_municipality_files():
    safe_mkdir(DATA_DIR)
    files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.lower().endswith(".xlsx")]
    files.sort()
    return files

def parse_muni_filename(filepath: str):
    base = os.path.basename(filepath)
    name = os.path.splitext(base)[0]
    m = re.match(r"^(\d+)[\-_](.+)$", name)
    if m:
        return m.group(1), m.group(2).replace("_", " ")
    return "0000", name.replace("_", " ")

# ------------------------------------------------------------
# SCHEMA / NORMALIZATION
# ------------------------------------------------------------

def _normalize_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["enviar_campo", "visitado"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].apply(lambda x: 1 if str(x).strip() in ["1", "True", "true", "SIM", "Sim"] else 0)
    return df

def _map_columns_to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    norm = {c: re.sub(r"\s+", " ", str(c)).strip().lower() for c in df.columns}

    targets = {
        "municipio_id": {"municipio_id", "município_id", "id_municipio", "id município"},
        "municipio_nome": {"municipio_nome", "município", "municipio", "município_nome", "nome_municipio", "nome município"},
        "item_id": {"item_id", "item id", "item_id.", "id_item", "id item", "Item_ID".lower()},
        "status": {"status", "situação", "situacao"},
        "categoria": {"categoria", "categoria do item"},
        "nome": {"nome", "nome do item", "item"},
        "endereco": {"endereco", "endereço", "endereço (rua, número etc.)", "logradouro"},
        "telefone": {"telefone", "fone", "contato", "telefone(s)"},
        "email": {"email", "e-mail", "e mail"},
        "site": {"site", "website", "url", "rede social", "site / rede social"},
        "latitude": {"latitude", "lat"},
        "longitude": {"longitude", "long", "lng"},
        "descricao": {"descricao", "descrição", "descrição do item", "observação geral", "descricao geral"},
        "validacao_preliminar": {"validacao_preliminar", "validação preliminar", "validacao preliminar", "validação", "validacao"},
        "obs_preliminar": {"obs_preliminar", "obs preliminar", "observações preliminares", "observacao preliminar", "obs gabinete", "observação gabinete"},
        "enviar_campo": {"enviar_campo", "enviar campo", "campo", "vai pra campo", "enviar para campo"},
        "visitado": {"visitado", "visitado?", "foi visitado"},
        "obs_campo": {"obs_campo", "obs campo", "observações de campo", "observacao campo"},
    }

    rename = {}
    for col, col_l in norm.items():
        for canon, variants in targets.items():
            if col_l in variants:
                rename[col] = canon
                break

    df = df.rename(columns=rename)

    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = "" if col not in ("enviar_campo", "visitado") else 0

    return df[CANONICAL_COLUMNS].copy()

def ensure_schema_soft(df: pd.DataFrame) -> pd.DataFrame:
    df = _map_columns_to_canonical(df)
    df = _normalize_flags(df)

    df["validacao_preliminar"] = df["validacao_preliminar"].fillna("Em branco").replace("", "Em branco")
    df["validacao_preliminar"] = df["validacao_preliminar"].apply(lambda x: x if x in VALIDATION_OPTIONS else "Em branco")

    df["status"] = df["status"].fillna("").replace("", "Inventariado INVTUR")
    df["status"] = df["status"].apply(lambda x: x if x in STATUS_OPTIONS else "Inventariado INVTUR")

    mask_empty = df["item_id"].astype(str).str.strip().eq("")
    if mask_empty.any():
        def _mk_id(row, seq):
            base = str(row.get("municipio_id", "")).strip() or "0000"
            return f"{base}-{seq:04d}"

        seq = 1
        new_ids = []
        for _, row in df.loc[mask_empty].iterrows():
            new_ids.append(_mk_id(row, seq))
            seq += 1
        df.loc[mask_empty, "item_id"] = new_ids

    return df

def compute_route_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    auto_route = df["validacao_preliminar"].isin(list(ROUTE_BY_VALIDATION)).astype(int)
    df["enviar_campo"] = ((df["enviar_campo"] == 1) | (auto_route == 1)).astype(int)
    df.loc[df["enviar_campo"] == 0, "visitado"] = 0
    return df

# ------------------------------------------------------------
# SESSION MASTER
# ------------------------------------------------------------

def _load_master_from_disk() -> pd.DataFrame:
    df_all = pd.read_excel(DATA_FILE, dtype=str)
    df_all = ensure_schema_soft(df_all)
    df_all = compute_route_flags(df_all)
    return df_all

def get_master_df() -> pd.DataFrame:
    mtime = os.path.getmtime(DATA_FILE) if os.path.exists(DATA_FILE) else None
    if "master_df" not in st.session_state or st.session_state.get("master_mtime") != mtime:
        st.session_state.master_df = _load_master_from_disk()
        st.session_state.master_mtime = mtime
        st.session_state.master_dirty = False
    return st.session_state.master_df

def mark_dirty():
    st.session_state.master_dirty = True

def save_master_df():
    st.session_state.master_df.to_excel(DATA_FILE, index=False)
    st.session_state.master_mtime = os.path.getmtime(DATA_FILE)
    st.session_state.master_dirty = False

def apply_row_updates(master_df: pd.DataFrame, edited_df: pd.DataFrame) -> pd.DataFrame:
    if edited_df is None or edited_df.empty:
        return master_df

    master_df = master_df.copy()

    # O editor não exibe o item_id (a coluna fica escondida pelo index).
    # Então, garantimos que o item_id exista no DataFrame retornado.
    edited = edited_df.copy()
    if "item_id" not in edited.columns:
        # 1) caso venha como Item_ID (por algum rename manual)
        if "Item_ID" in edited.columns:
            edited = edited.rename(columns={"Item_ID": "item_id"})
        else:
            # 2) caso o item_id esteja no index
            edited = edited.reset_index().rename(columns={"index": "item_id"})

    # Normaliza tipo e elimina duplicados
    edited["item_id"] = edited["item_id"].astype(str)
    edited = edited.drop_duplicates(subset=["item_id"], keep="first").copy()

    master_df["item_id"] = master_df["item_id"].astype(str)
    edited["item_id"] = edited["item_id"].astype(str)

    master_df = master_df.set_index("item_id", drop=False)
    edited = edited.set_index("item_id", drop=False)

    cols_updatable = [
        "endereco", "telefone", "latitude", "longitude",
        "validacao_preliminar", "obs_preliminar",
        "enviar_campo",
    ]
    idx_common = master_df.index.intersection(edited.index)
    for col in cols_updatable:
        if col in master_df.columns and col in edited.columns:
            master_df.loc[idx_common, col] = edited.loc[idx_common, col]

    master_df = master_df.reset_index(drop=True)
    master_df = ensure_schema_soft(master_df)
    master_df = compute_route_flags(master_df)
    return master_df

# ------------------------------------------------------------
# METRICS / CHARTS
# ------------------------------------------------------------

def kpis(df: pd.DataFrame):
    total = len(df)
    sim = int((df["validacao_preliminar"] == "Sim").sum())
    pend = int((df["validacao_preliminar"] == "Pendente").sum())
    nao = int((df["validacao_preliminar"] == "Não").sum())
    branco = int((df["validacao_preliminar"] == "Em branco").sum())
    return {
        "total": total,
        "val_sim": sim,
        "val_pendente": pend,
        "val_nao_ou_branco": nao + branco,
        "stats_validacao": {"Sim": sim, "Pendente": pend, "Não": nao, "Em branco": branco},
    }

def render_kpis(k):
    st.markdown(
        f"""
        <div class="kpi-grid">
          <div class="kpi bar-slate">
            <div class="kpi-label">Total de Itens</div>
            <div class="kpi-value">{k["total"]}</div>
            <div class="kpi-foot">Base filtrada</div>
          </div>
          <div class="kpi bar-emerald">
            <div class="kpi-label">Validação • Sim</div>
            <div class="kpi-value" style="color: var(--emerald)">{k["val_sim"]}</div>
            <div class="kpi-foot">Confirmados</div>
          </div>
          <div class="kpi bar-amber">
            <div class="kpi-label">Validação • Pendente</div>
            <div class="kpi-value" style="color: var(--amber)">{k["val_pendente"]}</div>
            <div class="kpi-foot">Em auditoria</div>
          </div>
          <div class="kpi bar-rose">
            <div class="kpi-label">Não / Em branco</div>
            <div class="kpi-value" style="color: var(--rose)">{k["val_nao_ou_branco"]}</div>
            <div class="kpi-foot">Lacunas / inválidos</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def donut_chart(title: str, data_dict: dict):
    df = pd.DataFrame({"label": list(data_dict.keys()), "value": list(data_dict.values())})
    fig = px.pie(df, names="label", values="value", hole=0.72)
    fig.update_layout(
        height=310,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        title=dict(text=title, x=0.02, font=dict(size=14, color="#0f172a")),
    )
    fig.update_traces(textinfo="percent+value", textfont=dict(color="#0f172a"))
    return fig

def categories_bar(df: pd.DataFrame, title: str = "Distribuição por Categorias Reais"):
    s = df["categoria"].fillna("Sem categoria").astype(str).str.strip()
    counts = s.value_counts().head(12)
    if counts.empty:
        st.info("Sem categorias para exibir.")
        return
    dfc = counts.reset_index()
    dfc.columns = ["categoria", "qtd"]
    dfc = dfc.sort_values("qtd", ascending=True)
    fig = px.bar(dfc, x="qtd", y="categoria", orientation="h")
    fig.update_layout(
        height=310,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title=dict(text=title, x=0.02, font=dict(size=14, color="#0f172a")),
        xaxis_title="Qtd",
        yaxis_title="",
        showlegend=False,
        # ===== AJUSTE PEDIDO: fonte das categorias em grafite =====
        yaxis=dict(tickfont=dict(color="#334155")),
        xaxis=dict(tickfont=dict(color="#334155")),
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
# FILTERS
# ------------------------------------------------------------

def apply_filters(df: pd.DataFrame, q: str, val_list, origin, cat_list, only_unvisited=False, only_route=False):
    out = df.copy()

    if q:
        ql = q.lower().strip()
        mask = (
            out["nome"].astype(str).str.lower().str.contains(ql, na=False) |
            out["categoria"].astype(str).str.lower().str.contains(ql, na=False) |
            out["descricao"].astype(str).str.lower().str.contains(ql, na=False) |
            out["endereco"].astype(str).str.lower().str.contains(ql, na=False)
        )
        out = out[mask]

    if val_list:
        out = out[out["validacao_preliminar"].isin(val_list)]

    if origin != "Todos":
        if origin == "INVTUR":
            out = out[out["status"] == "Inventariado INVTUR"]
        elif origin == "Novo":
            out = out[out["status"] == "Novo"]

    if cat_list:
        out = out[out["categoria"].isin(cat_list)]

    if only_route:
        out = out[out["enviar_campo"] == 1]

    if only_unvisited:
        out = out[(out["enviar_campo"] == 1) & (out["visitado"] == 0)]

    return out

# ------------------------------------------------------------
# EDITORS
# ------------------------------------------------------------

def editor_gabinete(df_view: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "municipio_nome",
        "status",
        "categoria",
        "nome",
        "endereco",
        "telefone",
        "latitude",
        "longitude",
        "email",
        "site",
        "descricao",
        "validacao_preliminar",
        "obs_preliminar",
        "enviar_campo",
    ]
    # Mantém item_id como chave (no index) sem exibir a coluna no app.
    base = df_view.copy()
    if "item_id" in base.columns:
        base = base.set_index("item_id", drop=False)
    else:
        # fallback: cria um id a partir do index original
        base = base.reset_index().rename(columns={"index": "item_id"}).set_index("item_id", drop=False)

    df_show = base[cols].copy()

    return st.data_editor(
        df_show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "municipio_nome": st.column_config.TextColumn("Município"),
            "status": st.column_config.TextColumn("Status"),
            "categoria": st.column_config.TextColumn("Categoria"),
            "nome": st.column_config.TextColumn("Nome do Item"),
            "endereco": st.column_config.TextColumn("Endereço"),
            "telefone": st.column_config.TextColumn("Telefone"),
            "latitude": st.column_config.TextColumn("Latitude"),
            "longitude": st.column_config.TextColumn("Longitude"),
            "email": st.column_config.TextColumn("E-mail"),
            "site": st.column_config.TextColumn("Site / Rede Social"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "validacao_preliminar": st.column_config.SelectboxColumn("Validação Preliminar", options=VALIDATION_OPTIONS, required=True),
            "obs_preliminar": st.column_config.TextColumn("Obs. Preliminar"),
            "enviar_campo": st.column_config.CheckboxColumn("Enviar Campo", help="Entra na rota (forçado)"),
        },
        disabled=["municipio_nome", "status", "categoria", "nome", "email", "site", "descricao"],
        num_rows="fixed",
        key="editor_gabinete",
    )

def editor_campo(df_view: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "municipio_nome",
        "categoria",
        "nome",
        "endereco",
        "telefone",
        "latitude",
        "longitude",
        "email",
        "site",
        "descricao",
        "validacao_preliminar",
        "obs_preliminar",
        "enviar_campo",
        "visitado",
        "obs_campo",
    ]
    # Mantém item_id como chave (no index) sem exibir a coluna no app.
    base = df_view.copy()
    if "item_id" in base.columns:
        base = base.set_index("item_id", drop=False)
    else:
        base = base.reset_index().rename(columns={"index": "item_id"}).set_index("item_id", drop=False)
    df_show = base[cols].copy()

    return st.data_editor(
        df_show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "municipio_nome": st.column_config.TextColumn("Município"),
            "categoria": st.column_config.TextColumn("Categoria"),
            "nome": st.column_config.TextColumn("Nome do Item"),
            "endereco": st.column_config.TextColumn("Endereço"),
            "telefone": st.column_config.TextColumn("Telefone"),
            "latitude": st.column_config.TextColumn("Latitude"),
            "longitude": st.column_config.TextColumn("Longitude"),
            "email": st.column_config.TextColumn("E-mail"),
            "site": st.column_config.TextColumn("Site / Rede Social"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "validacao_preliminar": st.column_config.TextColumn("Validação Preliminar"),
            "obs_preliminar": st.column_config.TextColumn("Obs. Preliminar"),
            "enviar_campo": st.column_config.CheckboxColumn("Enviar Campo"),
            "visitado": st.column_config.CheckboxColumn("Visitado"),
            "obs_campo": st.column_config.TextColumn("Obs. Campo"),
        },
        disabled=[
            "municipio_nome", "categoria", "nome",
            "validacao_preliminar", "obs_preliminar",
            "visitado", "obs_campo",
        ],
        num_rows="fixed",
        key="editor_campo",
    )

# ------------------------------------------------------------
# NAV + MUNICIPIO OPTIONS
# ------------------------------------------------------------

def _municipio_options(master_df: pd.DataFrame):
    muni_list = sorted(master_df["municipio_nome"].dropna().unique().tolist())
    options = ["Todos (consolidado)"] + muni_list
    return options

# ------------------------------------------------------------
# PAGES
# ------------------------------------------------------------

def page_gabinete(master_df: pd.DataFrame, df_scope: pd.DataFrame, municipio_nome: str) -> pd.DataFrame:
    render_hero(municipio_nome, "Pesquisa de Gabinete")

    q_init = st.session_state.get("g_q", "")
    val_init = st.session_state.get("g_val", [])
    origin_init = st.session_state.get("g_origin", "Todos")
    cat_init = st.session_state.get("g_cat", [])

    df_filtered_init = apply_filters(df_scope, q_init, val_init, origin_init, cat_init)
    k = kpis(df_filtered_init)
    render_kpis(k)

    c1, c2 = st.columns([1.6, 1], gap="large")
    with c1:
        categories_bar(df_filtered_init, "Distribuição por Categorias Reais")
    with c2:
        st.plotly_chart(donut_chart("Progresso da Validação Preliminar", k["stats_validacao"]), use_container_width=True)

    with st.container(border=True):
        st.markdown("### Filtros")

        # ===== AJUSTE: botões de página visíveis (retangulares) acima do Município + status "Tudo salvo" =====
        dirty = bool(st.session_state.get("master_dirty", False))
        options = _municipio_options(master_df)

        # Linha 1: Botões de página (esquerda) + status pill (direita)
        r1 = st.columns([1.35, 1.35, 3.3, 1.2], gap="medium")
        with r1[0]:
            is_active = st.session_state.get("ui_page", "Pesquisa de Gabinete") == "Pesquisa de Gabinete"
            if st.button("Pesquisa de Gabinete", use_container_width=True, type=("primary" if is_active else "secondary")):
                st.session_state.ui_page = "Pesquisa de Gabinete"
                st.rerun()
        with r1[1]:
            is_active = st.session_state.get("ui_page", "Pesquisa de Gabinete") == "Gestão de Campo"
            if st.button("Gestão de Campo", use_container_width=True, type=("primary" if is_active else "secondary")):
                st.session_state.ui_page = "Gestão de Campo"
                st.rerun()
        with r1[2]:
            st.write("")
        with r1[3]:
            render_status_pill(dirty)

        # Linha 2: Município + Busca + Validação + Origem + Categoria
        f0, f1, f2, f3, f4 = st.columns([2.3, 2.3, 1.8, 1.4, 2.0], gap="medium")
        with f0:
            st.selectbox("Município", options, key="ui_muni")
        with f1:
            q = st.text_input("Busca global", placeholder="Nome, categoria, descrição ou endereço...", key="g_q")
        with f2:
            val_multi = st.multiselect("Validação (multi)", VALIDATION_OPTIONS, default=st.session_state.get("g_val", []), key="g_val")
        with f3:
            origin = st.selectbox("Origem", ["Todos", "INVTUR", "Novo"], index=0, key="g_origin")
        with f4:
            cats = sorted(df_scope["categoria"].fillna("Sem categoria").astype(str).str.strip().unique().tolist())
            cat_multi = st.multiselect("Categoria (multi)", cats, default=st.session_state.get("g_cat", []), key="g_cat")

    df_filtered = apply_filters(df_scope, q, val_multi, origin, cat_multi)

    # ===== AJUSTE PEDIDO: reduzir espaço entre filtros e tabela =====
    st.markdown('<div style="margin-top:-26px;"></div>', unsafe_allow_html=True)

    st.markdown("### Tabela (Gabinete)")
    st.caption("Edite: Endereço, Telefone, Latitude, Longitude, Validação Preliminar, Obs Preliminar e Enviar Campo.")
    return editor_gabinete(df_filtered)

def page_campo(master_df: pd.DataFrame, df_scope: pd.DataFrame, municipio_nome: str) -> pd.DataFrame:
    render_hero(municipio_nome, "Gestão de Campo")

    df_route = df_scope[df_scope["enviar_campo"] == 1].copy()

    total_rota = len(df_route)
    visitados = int((df_route["visitado"] == 1).sum())
    a_visitar = int((df_route["visitado"] == 0).sum())

    c1, c2, c3 = st.columns(3, gap="medium")
    c1.metric("Itens na rota", total_rota)
    c2.metric("Visitados", visitados)
    c3.metric("A visitar", a_visitar)

    q_init = st.session_state.get("c_q", "")
    origin_init = st.session_state.get("c_origin", "Todos")
    only_unvisited_init = st.session_state.get("c_only_unvisited", False)
    cat_init = st.session_state.get("c_cat", [])

    df_route_init = apply_filters(df_route, q_init, val_list=None, origin=origin_init, cat_list=cat_init, only_unvisited=only_unvisited_init)

    c1, c2 = st.columns([1.6, 1], gap="large")
    with c1:
        categories_bar(df_route_init, "Categorias na Rota (informativo)")
    with c2:
        st.plotly_chart(
            donut_chart(
                "Status de Campo (informativo)",
                {"Visitado": int((df_route_init["visitado"] == 1).sum()), "A visitar": int((df_route_init["visitado"] == 0).sum())},
            ),
            use_container_width=True,
        )

    with st.container(border=True):
        st.markdown("### Filtros")

        dirty = bool(st.session_state.get("master_dirty", False))
        options = _municipio_options(master_df)

        # Linha 1: botões de página (esquerda) + status pill (direita)
        t1, t2, t3 = st.columns([2.6, 3.0, 1.4], gap="medium")
        with t1:
            b1, b2 = st.columns(2, gap="small")
            with b1:
                if st.button("Pesquisa de Gabinete", use_container_width=True, type=("primary" if st.session_state.get("ui_page", "Pesquisa de Gabinete") == "Pesquisa de Gabinete" else "secondary")):
                    st.session_state.ui_page = "Pesquisa de Gabinete"
                    st.rerun()
            with b2:
                if st.button("Gestão de Campo", use_container_width=True, type=("primary" if st.session_state.get("ui_page", "Pesquisa de Gabinete") == "Gestão de Campo" else "secondary")):
                    st.session_state.ui_page = "Gestão de Campo"
                    st.rerun()
        with t2:
            st.write("")
        with t3:
            render_status_pill(dirty)

        # Linha 2: Município + Busca + Origem + Somente a visitar + Categoria
        f0, f1, f2, f3, f4 = st.columns([2.6, 2.2, 1.4, 1.4, 1.8], gap="medium")
        with f0:
            st.selectbox("Município", options, key="ui_muni")
        with f1:
            q = st.text_input("Busca", placeholder="Nome, categoria, endereço...", key="c_q")
        with f2:
            origin = st.selectbox("Origem", ["Todos", "INVTUR", "Novo"], index=0, key="c_origin")
        with f3:
            only_unvisited = st.checkbox("Somente a visitar", value=st.session_state.get("c_only_unvisited", False), key="c_only_unvisited")
        with f4:
            cats = sorted(df_route["categoria"].fillna("Sem categoria").astype(str).str.strip().unique().tolist())
            cat_multi = st.multiselect("Categoria (multi)", cats, default=st.session_state.get("c_cat", []), key="c_cat")



    df_route_f = apply_filters(df_route, q, val_list=None, origin=origin, cat_list=cat_multi, only_unvisited=only_unvisited)

    # ===== AJUSTE PEDIDO: reduzir espaço entre filtros e tabela =====
    # Reduz o espaçamento entre filtros e tabela
    st.markdown('<div style="margin-top:-26px;"></div>', unsafe_allow_html=True)

    st.markdown("### Rota (itens enviados para campo)")
    st.caption("Nesta fase, Visitado e Obs Campo ainda não editáveis (serão liberados na próxima etapa).")
    return editor_campo(df_route_f)

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    st.set_page_config(page_title="EMPETUR | Gabinete + Campo", layout="wide")
    inject_css()
    render_topbar()

    if not os.path.exists(DATA_FILE):
        st.error("Arquivo consolidado não encontrado.")
        st.caption(DATA_FILE)
        st.stop()

    master_df = get_master_df()

    if "ui_page" not in st.session_state:
        st.session_state.ui_page = "Pesquisa de Gabinete"
    if "ui_muni" not in st.session_state:
        st.session_state.ui_muni = "Todos (consolidado)"

    page = st.session_state.get("ui_page", "Pesquisa de Gabinete")
    chosen = st.session_state.get("ui_muni", "Todos (consolidado)")

    options = _municipio_options(master_df)
    if chosen not in options:
        chosen = "Todos (consolidado)"
        st.session_state.ui_muni = chosen

    viewing_all = (chosen == "Todos (consolidado)")

    if viewing_all:
        municipio_nome = "Todos"
        scope_df = master_df.copy()
    else:
        municipio_nome = chosen
        scope_df = master_df[master_df["municipio_nome"] == municipio_nome].copy()

    scope_df = compute_route_flags(scope_df)

    if page == "Pesquisa de Gabinete":
        edited = page_gabinete(master_df, scope_df, municipio_nome)
    else:
        edited = page_campo(master_df, scope_df, municipio_nome)

    if edited is not None and not edited.empty:
        if viewing_all:
            new_master = apply_row_updates(master_df, edited)
        else:
            scope_after = apply_row_updates(scope_df, edited)
            other = master_df[master_df["municipio_nome"] != municipio_nome].copy()
            new_master = pd.concat([other, scope_after], ignore_index=True)
            new_master = ensure_schema_soft(new_master)
            new_master = compute_route_flags(new_master)

        if not new_master.equals(master_df):
            st.session_state.master_df = new_master
            mark_dirty()

    st.write("")
    with st.container(border=True):
        dirty = bool(st.session_state.get("master_dirty", False))
        a1, a2 = st.columns([1, 1], gap="medium")

        with a1:
            st.button(
                "💾 Salvar alterações (consolidado)",
                use_container_width=True,
                disabled=(not dirty),
                on_click=save_master_df if dirty else None,
            )
        with a2:
            rota_df = compute_route_flags(scope_df)
            rota_df = rota_df[rota_df["enviar_campo"] == 1].copy()
            rota_df = rota_df.sort_values(
                by=["municipio_nome", "visitado", "validacao_preliminar", "nome"],
                ascending=[True, True, True, True],
            )
            output = BytesIO()
            rota_df.to_excel(output, index=False)
            fname = "ROTA_ALL_Consolidado.xlsx" if viewing_all else f"ROTA_{municipio_nome.replace(' ','_')}.xlsx"

            st.download_button(
                "📦 Baixar Rota (Excel)",
                data=output.getvalue(),
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    st.caption(f"Última renderização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()
