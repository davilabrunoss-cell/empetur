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
  slugify,
  uniqueValues,
} from "./lib/dashboard";

const FILTER_KEYS = ["regiao", "municipio", "questionario", "categoria", "pesquisador", "search"];

function useDashboardData() {
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    fetch("/data/dashboard_payload.json")
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

function Shell({ children, generatedAt }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <div className="brand-logo">
            <img src="/assets/logo_agora.png" alt="Ágora Pesquisa" />
          </div>
          <div>
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

function KpiCard({ label, value, help }) {
  return (
    <article className="kpi-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{help}</small>
    </article>
  );
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

function HorizontalBars({ title, subtitle, items, labelKey }) {
  const max = Math.max(...items.map((item) => item.total), 1);
  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>
      <div className="bars-list">
        {items.map((item) => (
          <div className="bar-row" key={`${item[labelKey]}-${item.total}`}>
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
        <KpiCard label="Municípios com coleta" value={formatNumber(municipiosComColeta)} help="Municípios com produção registrada" />
        <KpiCard label="Questionários" value={formatNumber(payload.resumo_questionarios.length)} help="Tipos de questionário com ocorrências" />
        <KpiCard label="Pesquisadores" value={formatNumber(payload.resumo_pesquisadores.length)} help="Responsáveis identificados na base" />
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
        <HorizontalBars
          title="Total por pesquisador"
          subtitle="Valores absolutos por responsável."
          items={payload.resumo_pesquisadores.slice(0, 12).map((item) => ({
            ...item,
            total: Number(item.total),
          }))}
          labelKey="pesquisador"
        />
        <HorizontalBars
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

function MunicipioPage({ payload }) {
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

  return (
    <>
      <section className="municipio-hero panel">
        <div>
          <Link className="back-link" to="/">
            Voltar ao mosaico
          </Link>
          <h2>{municipioMeta.municipio}</h2>
          <p>{municipioMeta.regiao}</p>
        </div>
        <div className="municipio-summary-pill">
          <span>Total coletado</span>
          <strong>{formatNumber(municipioRows.length)}</strong>
        </div>
      </section>

      <section className="kpi-grid">
        <KpiCard label="Questionários preenchidos" value={formatNumber(detail.totalQuestionarios)} help="Total de registros do município" />
        <KpiCard label="Primeira coleta" value={formatDateTime(detail.primeiraColeta)} help="Data inicial encontrada" />
        <KpiCard label="Última coleta" value={formatDateTime(detail.ultimaColeta)} help="Data mais recente encontrada" />
        <KpiCard label="Total previsto" value={formatNumber(municipioMeta.total_previsto)} help="Campo preparado para futura apuração" />
      </section>

      <div className="dual-grid">
        <HorizontalBars
          title="Total por categoria"
          subtitle="Distribuição da produção dentro do município."
          items={detail.categorias}
          labelKey="categoria"
        />
        <HorizontalBars
          title="Total por pesquisador"
          subtitle="Produção por pesquisador no município."
          items={detail.pesquisadores}
          labelKey="pesquisador"
        />
      </div>

      <DataTable rows={municipioRows} fileName={`empetur-${slugify(municipioMeta.municipio)}.csv`} />
    </>
  );
}

export default function App() {
  const { payload, error } = useDashboardData();

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
        <Route path="/municipio/:municipioSlug" element={<MunicipioPage payload={payload} />} />
      </Routes>
    </Shell>
  );
}
