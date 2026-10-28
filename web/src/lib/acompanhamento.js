import plano from "../data/acompanhamento-provisorio.json";
import { slugify } from "./dashboard";

function normalizeName(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function formFor(row) {
  return plano.formulariosPorProjeto[String(row.codigo_pesquisa)] ||
    plano.formulariosPorNome[row.questionario_preenchido] || "";
}

export function buildAcompanhamento(municipioSlug, coletas) {
  const planned = plano.itens.filter((item) => slugify(item.municipio) === municipioSlug);
  if (!planned.length) return null;

  const liveRows = coletas.filter((row) => row.municipio_slug === municipioSlug);
  const rowsById = new Map(liveRows.map((row) => [String(row.nro_identificacao || ""), row]));
  const assigned = new Set();
  const results = planned.map((item) => {
    const matched = item.realizados
      .map((id) => rowsById.get(id))
      .filter((row) => row && formFor(row) === item.questionario);
    matched.forEach((row) => assigned.add(String(row.nro_identificacao)));
    return { ...item, status: matched.length ? "realizado" : "pendente", coletas: matched };
  });

  // Only unique, exact name+form matches are inferred; similar names require human review.
  for (const row of liveRows) {
    const id = String(row.nro_identificacao || "");
    if (!id || assigned.has(id)) continue;
    const form = formFor(row);
    if (!form) continue;
    const candidates = results.filter((item) =>
      item.status === "pendente" && item.questionario === form &&
      normalizeName(item.atrativo) === normalizeName(row.nome_atrativo));
    if (candidates.length !== 1) continue;
    candidates[0].status = "realizado";
    candidates[0].coletas = [row];
    assigned.add(id);
  }

  for (const item of results) {
    if (item.status === "realizado") continue;
    const conflicts = item.outroFormulario
      .map((id) => rowsById.get(id))
      .filter((row) => row && formFor(row) !== item.questionario);
    if (conflicts.length) {
      item.status = "outro-formulario";
      item.coletas = conflicts;
    }
  }

  const revisar = liveRows.filter((row) => !assigned.has(String(row.nro_identificacao || "")));
  return {
    versao: plano.versao,
    itens: results,
    revisar,
    totais: {
      previstos: results.length,
      realizados: results.filter((item) => item.status === "realizado").length,
      outroFormulario: results.filter((item) => item.status === "outro-formulario").length,
      semVinculo: results.filter((item) => item.status === "pendente").length,
    },
  };
}
