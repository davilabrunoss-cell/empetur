const COLLATOR = new Intl.Collator("pt-BR");

export function slugify(value) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function parseBrDateTime(value) {
  if (!value) return null;
  const [datePart, timePart = "00:00:00"] = value.split(" ");
  const [day, month, year] = datePart.split("/").map(Number);
  const [hour = 0, minute = 0, second = 0] = timePart.split(":").map(Number);
  return new Date(year, month - 1, day, hour, minute, second);
}

export function formatDateTime(value) {
  if (!value) return "Sem coleta";
  const date = value instanceof Date ? value : parseBrDateTime(value);
  if (!date || Number.isNaN(date.getTime())) return "Sem coleta";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(date);
}

export function formatNumber(value) {
  return new Intl.NumberFormat("pt-BR").format(Number(value || 0));
}

export function compareText(a, b) {
  return COLLATOR.compare(a ?? "", b ?? "");
}

export function buildHomeRows(payload) {
  const regionByMunicipio = new Map(
    payload.cadastro_municipios.map((item) => [item.municipio, item.regiao]),
  );

  return payload.base_rows.map((row, index) => ({
    ...row,
    id: `${row.arquivo_origem}-${row.linha_origem}-${index}`,
    regiao: regionByMunicipio.get(row.municipio) ?? "",
    municipio_slug: slugify(row.municipio),
  }));
}

export function groupMunicipios(payload) {
  return payload.resumo_municipios.reduce((acc, item) => {
    if (!acc[item.regiao]) {
      acc[item.regiao] = [];
    }
    acc[item.regiao].push({
      ...item,
      total_realizado_num: Number(item.total_realizado || 0),
      total_previsto_num: Number(item.total_previsto || 0),
      municipio_slug: slugify(item.municipio),
    });
    acc[item.regiao].sort((a, b) => Number(a.ordem_municipio) - Number(b.ordem_municipio));
    return acc;
  }, {});
}

export function buildMunicipioLookup(payload) {
  const map = new Map();
  for (const item of payload.resumo_municipios) {
    map.set(slugify(item.municipio), item);
  }
  return map;
}

export function uniqueValues(rows, key) {
  return [...new Set(rows.map((row) => row[key]).filter(Boolean))].sort(compareText);
}

export function filterRows(rows, filters) {
  const search = filters.search.trim().toLowerCase();
  return rows.filter((row) => {
    if (filters.regiao && row.regiao !== filters.regiao) return false;
    if (filters.municipio && row.municipio !== filters.municipio) return false;
    if (filters.questionario && row.questionario_preenchido !== filters.questionario) return false;
    if (filters.categoria && row.categoria !== filters.categoria) return false;
    if (filters.pesquisador && row.pesquisador !== filters.pesquisador) return false;

    if (!search) return true;
    const haystack = [
      row.municipio,
      row.regiao,
      row.questionario_preenchido,
      row.categoria,
      row.nome_atrativo,
      row.pesquisador,
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(search);
  });
}

export function downloadCsv(rows, fileName) {
  const headers = [
    "regiao",
    "municipio",
    "questionario_preenchido",
    "categoria",
    "nome_atrativo",
    "pesquisador",
    "data_inicio_coleta",
    "data_fim_coleta",
    "arquivo_origem",
    "linha_origem",
  ];

  const escapeCsv = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;
  const lines = [headers.join(",")];
  for (const row of rows) {
    lines.push(headers.map((header) => escapeCsv(row[header])).join(","));
  }

  const blob = new Blob(["\ufeff" + lines.join("\n")], {
    type: "text/csv;charset=utf-8;",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function computeMunicipioDetail(rows) {
  const totalQuestionarios = rows.length;
  const categorias = Object.entries(
    rows.reduce((acc, row) => {
      acc[row.categoria] = (acc[row.categoria] ?? 0) + 1;
      return acc;
    }, {}),
  )
    .map(([categoria, total]) => ({ categoria, total }))
    .sort((a, b) => b.total - a.total || compareText(a.categoria, b.categoria));

  const pesquisadores = Object.entries(
    rows.reduce((acc, row) => {
      acc[row.pesquisador] = (acc[row.pesquisador] ?? 0) + 1;
      return acc;
    }, {}),
  )
    .map(([pesquisador, total]) => ({ pesquisador, total }))
    .sort((a, b) => b.total - a.total || compareText(a.pesquisador, b.pesquisador));

  const dates = rows
    .map((row) => parseBrDateTime(row.data_inicio_coleta))
    .filter((date) => date instanceof Date && !Number.isNaN(date.getTime()))
    .sort((a, b) => a - b);

  return {
    totalQuestionarios,
    categorias,
    pesquisadores,
    primeiraColeta: dates[0] ?? null,
    ultimaColeta: dates[dates.length - 1] ?? null,
  };
}

