import { useEffect, useMemo, useState } from "react";
import { Link, Navigate, Route, Routes, useParams } from "react-router-dom";
import {
  buildHomeRows,
  buildMunicipioLookup,
  compareText,
  computeMunicipioDetail,
  downloadCsv,
  filterRows,
  formatDateTime,
  formatNumber,
  groupMunicipios,
  parseBrDateTime,
  slugify,
  uniqueValues,
} from "./lib/dashboard";

const CONCLUDED_STORAGE_KEY = "empetur-municipios-concluidos";
const DASHBOARD_DATA_URL =
  import.meta.env.VITE_DASHBOARD_DATA_URL || "/data/dashboard_payload.json";

function useDashboardData() {
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    fetch(DASHBOARD_DATA_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Falha ao carregar os dados do dashboard.");
        }
        return response.json();
      })
      .then((data) => {
        if (active) setPayload(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, []);

  return { payload, error };
}

function useConcludedMunicipios() {
  const [concluded, setConcluded] = useState({});

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(CONCLUDED_STORAGE_KEY);
      if (saved) {
        setConcluded(JSON.parse(saved));
      }
    } catch (error) {
      console.error("Falha ao carregar status concluído", error);
    }
  }, []);

  const update = (municipioSlug, isConcluded) => {
    setConcluded((current) => {
      const next = { ...current, [municipioSlug]: isConcluded };
      window.localStorage.setItem(CONCLUDED_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  return { concluded, update };
}

function differenceInDays(referenceDate, targetDate) {
  if (!referenceDate || !targetDate) return 0;
  const start = new Date(referenceDate.getFullYear(), referenceDate.getMonth(), referenceDate.getDate());
  const end = new Date(targetDate.getFullYear(), targetDate.getMonth(), targetDate.getDate());
  return Math.floor((start - end) / (1000 * 60 * 60 * 24));
}

function buildMunicipiosStatus(payload, rows, concludedMap) {
  const statusWeight = {
    Ativo: 0,
    Alerta: 1,
    "Não Iniciado": 2,
    Concluído: 3,
  };

  const generatedAt = parseBrDateTime(payload.generated_at);
  const byMunicipio = rows.reduce((acc, row) => {
    if (!acc[row.municipio]) acc[row.municipio] = [];
    acc[row.municipio].push(row);
    return acc;
  }, {});

  return payload.resumo_municipios
    .map((item) => {
      const municipioRows = byMunicipio[item.municipio] ?? [];
      const municipioSlug = slugify(item.municipio);
      const dates = municipioRows
        .map((row) => parseBrDateTime(row.data_inicio_coleta))
        .filter((date) => date instanceof Date && !Number.isNaN(date.getTime()))
        .sort((a, b) => a - b);

      const uniqueFieldDays = new Set(
        municipioRows
          .map((row) => row.data_inicio_coleta?.split(" ")[0] ?? "")
          .filter(Boolean),
      );

      const lastCollection = dates[dates.length - 1] ?? null;
      const concluded = Boolean(concludedMap[municipioSlug]);

      let status = "Ativo";
      if (concluded) {
        status = "Concluído";
      } else if (municipioRows.length === 0) {
        status = "Não Iniciado";
      } else if (differenceInDays(generatedAt, lastCollection) > 3) {
        status = "Alerta";
      }

      return {
        ...item,
        municipioSlug,
        status,
        totalColetas: municipioRows.length,
        totalDiasCampo: uniqueFieldDays.size,
        ultimaColeta: lastCollection,
        concluded,
      };
    })
    .sort((a, b) => {
      const statusDiff = (statusWeight[a.status] ?? 99) - (statusWeight[b.status] ?? 99);
      if (statusDiff !== 0) return statusDiff;
      return compareText(a.municipio, b.municipio);
    });
}

function buildPesquisadoresSummary(rows) {
  const byPesquisador = rows.reduce((acc, row) => {
    if (!row.pesquisador) return acc;
    if (!acc[row.pesquisador]) {
      acc[row.pesquisador] = [];
    }
    acc[row.pesquisador].push(row);
    return acc;
  }, {});

  return Object.entries(byPesquisador)
    .map(([pesquisador, pesquisadorRows]) => {
      const municipios = new Set(pesquisadorRows.map((row) => row.municipio).filter(Boolean));
      const dates = pesquisadorRows
        .map((row) => parseBrDateTime(row.data_inicio_coleta))
        .filter((date) => date instanceof Date && !Number.isNaN(date.getTime()))
        .sort((a, b) => a - b);

      return {
        pesquisador,
        totalColetas: pesquisadorRows.length,
        totalMunicipios: municipios.size,
        ultimaColeta: dates[dates.length - 1] ?? null,
      };
    })
    .sort((a, b) => b.totalColetas - a.totalColetas || compareText(a.pesquisador, b.pesquisador));
}

function getMunicipioStatusLabel(payload, rows, concludedMap, municipioNome) {
  const items = buildMunicipiosStatus(payload, rows, concludedMap);
  return items.find((item) => item.municipio === municipioNome)?.status ?? "Não Iniciado";
}

function Shell({ children, generatedAt }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <div className="brand-logo">
            <img src="/assets/logo_agora.png" alt="Ágora Pesquisa" />
          </div>
          <div className="brand-copy">
            <p className="eyebrow">Dashboard de Produção de Campo</p>
            <h1>Inventário Turístico de Pernambuco | EMPETUR</h1>
          </div>
        </div>
        <div className="header-meta">
          <span>Atualização da carga</span>
          <strong>{generatedAt ?? "Carregando..."}</strong>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}

function KpiCard({ label, value, help, href }) {
  const content = (
    <>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{help}</small>
    </>
  );

  if (href) {
    return (
      <Link className="kpi-card kpi-card-link" to={href}>
        {content}
      </Link>
    );
  }

  return <article className="kpi-card">{content}</article>;
}

function MunicipioCard({ item }) {
  return (
    <Link className="municipio-card" to={`/municipio/${item.municipio_slug}`}>
      <span className="municipio-region">{item.regiao}</span>
      <strong>{item.municipio}</strong>
      <div className="municipio-total">
        <small>Total coletado</small>
        <span>{formatNumber(item.total_realizado_num)}</span>
      </div>
    </Link>
  );
}

function Filters({ rows, filters, setFilters, municipalityOptions }) {
  const options = {
    regiao: uniqueValues(rows, "regiao"),
    municipio: municipalityOptions,
    questionario: uniqueValues(rows, "questionario_preenchido"),
    categoria: uniqueValues(rows, "categoria"),
    pesquisador: uniqueValues(rows, "pesquisador"),
  };

  const setValue = (key, value) => setFilters((current) => ({ ...current, [key]: value }));

  return (
    <section className="panel filters-panel">
      <div className="panel-heading">
        <div>
          <h2>Tabela consolidada</h2>
          <p>Filtre a base por município, categoria, questionário ou pesquisador.</p>
        </div>
      </div>
      <div className="filters-grid">
        <label>
          <span>Região</span>
          <select value={filters.regiao} onChange={(e) => setValue("regiao", e.target.value)}>
            <option value="">Todas</option>
            {options.regiao.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Município</span>
          <select value={filters.municipio} onChange={(e) => setValue("municipio", e.target.value)}>
            <option value="">Todos</option>
            {options.municipio.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Questionário</span>
          <select value={filters.questionario} onChange={(e) => setValue("questionario", e.target.value)}>
            <option value="">Todos</option>
            {options.questionario.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Categoria</span>
          <select value={filters.categoria} onChange={(e) => setValue("categoria", e.target.value)}>
            <option value="">Todas</option>
            {options.categoria.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Pesquisador</span>
          <select value={filters.pesquisador} onChange={(e) => setValue("pesquisador", e.target.value)}>
            <option value="">Todos</option>
            {options.pesquisador.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label className="search-field">
          <span>Busca textual</span>
          <input
            type="search"
            placeholder="Nome, município, categoria ou pesquisador"
            value={filters.search}
            onChange={(e) => setValue("search", e.target.value)}
          />
        </label>
      </div>
    </section>
  );
}

function DataTable({ rows, fileName }) {
  return (
    <section className="panel table-panel">
      <div className="panel-heading">
        <div>
          <h2>Registros detalhados</h2>
          <p>{formatNumber(rows.length)} registros exibidos.</p>
        </div>
        <button className="ghost-button" onClick={() => downloadCsv(rows, fileName)}>
          Baixar CSV
        </button>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Região</th>
              <th>Município</th>
              <th>Questionário</th>
              <th>Categoria</th>
              <th>Nome do atrativo</th>
              <th>Pesquisador</th>
              <th>Data início</th>
              <th>Data fim</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.regiao}</td>
                <td>{row.municipio}</td>
                <td>{row.questionario_preenchido}</td>
                <td>{row.categoria}</td>
                <td>{row.nome_atrativo}</td>
                <td>{row.pesquisador}</td>
                <td>{row.data_inicio_coleta}</td>
                <td>{row.data_fim_coleta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ScrollMetricList({ title, subtitle, items, labelKey }) {
  const max = Math.max(...items.map((item) => item.total), 1);
  return (
    <section className="panel chart-panel compact-chart-panel">
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>
      <div className="scroll-metric-list">
        {items.map((item) => (
          <div className="bar-row compact-bar-row" key={`${item[labelKey]}-${item.total}`}>
            <div className="bar-meta">
              <strong>{item[labelKey]}</strong>
              <span>{formatNumber(item.total)}</span>
            </div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${(item.total / max) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function PageHero({ backTo, backLabel, title, subtitle }) {
  return (
    <section className="page-hero panel">
      <Link className="back-link" to={backTo}>
        {backLabel}
      </Link>
      <h2>{title}</h2>
      <p>{subtitle}</p>
    </section>
  );
}

function PageHeroWithSummary({ backTo, backLabel, title, subtitle, items }) {
  return (
    <section className="page-hero panel">
      <div className="page-hero-top">
        <div>
          <Link className="back-link" to={backTo}>
            {backLabel}
          </Link>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <div className="status-summary-grid">
          {items.map((item) => (
            <div className="status-summary-card" key={item.label}>
              <span>{item.label}</span>
              <strong>{formatNumber(item.value)}</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function HomePage({ payload }) {
  const homeRows = useMemo(() => buildHomeRows(payload), [payload]);
  const grouped = useMemo(() => groupMunicipios(payload), [payload]);
  const [filters, setFilters] = useState({
    regiao: "",
    municipio: "",
    questionario: "",
    categoria: "",
    pesquisador: "",
    search: "",
  });

  const filteredRows = useMemo(() => filterRows(homeRows, filters), [homeRows, filters]);
  const municipalityOptions = useMemo(
    () => payload.resumo_municipios.map((item) => item.municipio).sort(compareText),
    [payload],
  );
  const totalRealizado = payload.base_rows.length;
  const municipiosComColeta = payload.resumo_municipios.filter((item) => Number(item.total_realizado) > 0).length;

  return (
    <>
      <section className="kpi-grid">
        <KpiCard label="Total coletado" value={formatNumber(totalRealizado)} help="Registros consolidados" />
        <KpiCard label="Municípios com coleta" value={formatNumber(municipiosComColeta)} help="Municípios com produção registrada" href="/municipios" />
        <KpiCard label="Questionários" value={formatNumber(payload.resumo_questionarios.length)} help="Tipos de questionário com ocorrências" />
        <KpiCard label="Pesquisadores" value={formatNumber(payload.resumo_pesquisadores.length)} help="Responsáveis identificados na base" href="/pesquisadores" />
      </section>

      <section className="panel mosaic-panel">
        <div className="panel-heading">
          <div>
            <h2>Mosaico de municípios</h2>
            <p>Os 31 municípios aparecem sempre. Clique em um card para abrir o detalhamento.</p>
          </div>
        </div>
        {Object.entries(grouped).map(([regiao, municipios]) => (
          <div className="region-block" key={regiao}>
            <div className="region-header">
              <h3>{regiao}</h3>
              <span>{municipios.length} municípios</span>
            </div>
            <div className="mosaic-grid">
              {municipios.map((item) => (
                <MunicipioCard item={item} key={item.municipio} />
              ))}
            </div>
          </div>
        ))}
      </section>

      <div className="dual-grid">
        <ScrollMetricList
          title="Total por pesquisador"
          subtitle="Valores absolutos por responsável."
          items={payload.resumo_pesquisadores.map((item) => ({
            ...item,
            total: Number(item.total),
          }))}
          labelKey="pesquisador"
        />
        <ScrollMetricList
          title="Total por questionário"
          subtitle="Questionários com maior produção até o momento."
          items={payload.resumo_questionarios.map((item) => ({
            ...item,
            total: Number(item.total),
          }))}
          labelKey="questionario_preenchido"
        />
      </div>

      <Filters rows={homeRows} filters={filters} setFilters={setFilters} municipalityOptions={municipalityOptions} />
      <DataTable rows={filteredRows} fileName="empetur-base-filtrada.csv" />
    </>
  );
}

function MunicipiosPage({ payload, concludedMap, setConcluded }) {
  const rows = useMemo(() => buildHomeRows(payload), [payload]);
  const municipios = useMemo(
    () => buildMunicipiosStatus(payload, rows, concludedMap),
    [payload, rows, concludedMap],
  );
  const summaryItems = useMemo(
    () => [
      { label: "Ativos", value: municipios.filter((item) => item.status === "Ativo").length },
      { label: "Em Alerta", value: municipios.filter((item) => item.status === "Alerta").length },
      { label: "À Iniciar", value: municipios.filter((item) => item.status === "Não Iniciado").length },
      { label: "Concluídos", value: municipios.filter((item) => item.status === "Concluído").length },
    ],
    [municipios],
  );

  return (
    <>
      <PageHeroWithSummary
        backTo="/"
        backLabel="Voltar ao painel"
        title="Municípios"
        subtitle="Acompanhamento operacional por município, com status, dias de campo e última coleta."
        items={summaryItems}
      />
      <section className="panel table-panel">
        <div className="panel-heading">
          <div>
            <h2>Status municipal</h2>
            <p>Ativo, Não Iniciado, Concluído ou Alerta, com base na produção mais recente.</p>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Status</th>
                <th>Município</th>
                <th>Total de coletas</th>
                <th>Total de dias de campo</th>
                <th>Última coleta realizada</th>
                <th>Concluir</th>
              </tr>
            </thead>
            <tbody>
              {municipios.map((item) => (
                <tr key={item.municipio}>
                  <td>
                    <span className={`status-pill status-${slugify(item.status)}`}>{item.status}</span>
                  </td>
                  <td>
                    <Link className="table-link" to={`/municipio/${item.municipioSlug}`}>
                      {item.municipio}
                    </Link>
                  </td>
                  <td>{formatNumber(item.totalColetas)}</td>
                  <td>{formatNumber(item.totalDiasCampo)}</td>
                  <td>{formatDateTime(item.ultimaColeta)}</td>
                  <td>
                    <select
                      className="inline-select"
                      value={item.concluded ? "concluido" : "andamento"}
                      onChange={(event) => setConcluded(item.municipioSlug, event.target.value === "concluido")}
                    >
                      <option value="andamento">Em andamento</option>
                      <option value="concluido">Concluído</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function PesquisadoresPage({ payload }) {
  const rows = useMemo(() => buildHomeRows(payload), [payload]);
  const pesquisadores = useMemo(() => buildPesquisadoresSummary(rows), [rows]);

  return (
    <>
      <PageHero
        backTo="/"
        backLabel="Voltar ao painel"
        title="Pesquisadores"
        subtitle="Produção consolidada por pesquisador, com municípios cobertos e última coleta."
      />
      <section className="panel table-panel">
        <div className="panel-heading">
          <div>
            <h2>Resumo por pesquisador</h2>
            <p>Leitura rápida de produtividade com base na carga mais recente.</p>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Pesquisador</th>
                <th>Total de coletas</th>
                <th>Municípios com atuação</th>
                <th>Última coleta realizada</th>
              </tr>
            </thead>
            <tbody>
              {pesquisadores.map((item) => (
                <tr key={item.pesquisador}>
                  <td>{item.pesquisador}</td>
                  <td>{formatNumber(item.totalColetas)}</td>
                  <td>{formatNumber(item.totalMunicipios)}</td>
                  <td>{formatDateTime(item.ultimaColeta)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function MunicipioDetailPage({ payload, concludedMap }) {
  const { municipioSlug } = useParams();
  const homeRows = useMemo(() => buildHomeRows(payload), [payload]);
  const lookup = useMemo(() => buildMunicipioLookup(payload), [payload]);
  const municipioMeta = lookup.get(municipioSlug);

  if (!municipioMeta) {
    return <Navigate to="/" replace />;
  }

  const municipioRows = homeRows
    .filter((row) => row.municipio_slug === municipioSlug)
    .sort((a, b) => compareText(a.categoria, b.categoria) || compareText(a.nome_atrativo, b.nome_atrativo));

  const detail = computeMunicipioDetail(municipioRows);
  const status = getMunicipioStatusLabel(payload, homeRows, concludedMap, municipioMeta.municipio);

  return (
    <>
      <section className="municipio-hero panel">
        <div className="municipio-hero-main">
          <div className="back-link-row">
            <Link className="back-link" to="/">
              Voltar ao mosaico
            </Link>
            <Link className="back-link" to="/municipios">
              Página de municípios
            </Link>
          </div>
          <div className="municipio-title-row">
            <h2>{municipioMeta.municipio}</h2>
            <span className={`status-pill status-${slugify(status)}`}>{status}</span>
          </div>
          <p>{municipioMeta.regiao}</p>
        </div>
        <div className="municipio-researchers">
          <span>Pesquisador{detail.pesquisadores.length > 1 ? "es" : ""}</span>
          <div className="municipio-researchers-list">
            {detail.pesquisadores.map((item) => (
              <div className="municipio-researcher-item" key={item.pesquisador}>
                <strong>{item.pesquisador}</strong>
                <small>{formatNumber(item.total)} coletado(s)</small>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="kpi-grid">
        <KpiCard label="Questionários preenchidos" value={formatNumber(detail.totalQuestionarios)} help="Total de registros do município" />
        <KpiCard label="Primeira coleta" value={formatDateTime(detail.primeiraColeta)} help="Data inicial encontrada" />
        <KpiCard label="Última coleta" value={formatDateTime(detail.ultimaColeta)} help="Data mais recente encontrada" />
        <KpiCard label="Total previsto" value={formatNumber(municipioMeta.total_previsto)} help="Campo preparado para futura apuração" />
      </section>

      <div className="dual-grid">
        <ScrollMetricList
          title="Total por categoria"
          subtitle="Distribuição da produção dentro do município."
          items={detail.categorias}
          labelKey="categoria"
        />
        <ScrollMetricList
          title="Quantidade por questionário preenchido"
          subtitle="Distribuição da produção por tipo de questionário."
          items={detail.questionarios}
          labelKey="questionario"
        />
      </div>

      <DataTable rows={municipioRows} fileName={`empetur-${slugify(municipioMeta.municipio)}.csv`} />
    </>
  );
}

export default function App() {
  const { payload, error } = useDashboardData();
  const { concluded, update } = useConcludedMunicipios();

  if (error) {
    return (
      <Shell generatedAt="">
        <section className="panel empty-state">
          <h2>Falha ao carregar o dashboard</h2>
          <p>{error}</p>
        </section>
      </Shell>
    );
  }

  if (!payload) {
    return (
      <Shell generatedAt="">
        <section className="panel empty-state">
          <h2>Carregando dashboard</h2>
          <p>Preparando mosaico, indicadores e tabela consolidada.</p>
        </section>
      </Shell>
    );
  }

  return (
    <Shell generatedAt={payload.generated_at}>
      <Routes>
        <Route path="/" element={<HomePage payload={payload} />} />
        <Route path="/municipios" element={<MunicipiosPage payload={payload} concludedMap={concluded} setConcluded={update} />} />
        <Route path="/pesquisadores" element={<PesquisadoresPage payload={payload} />} />
        <Route path="/municipio/:municipioSlug" element={<MunicipioDetailPage payload={payload} concludedMap={concluded} />} />
      </Routes>
    </Shell>
  );
}
