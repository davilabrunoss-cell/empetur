create table if not exists public.empetur_tabela_base (
  id bigint generated always as identity primary key,
  arquivo_origem text not null default '',
  codigo_pesquisa text not null,
  questionario_preenchido text not null default '',
  nro_identificacao text not null,
  municipio text not null default '',
  categoria text not null default '',
  nome_atrativo text not null default '',
  pesquisador_informado text not null default '',
  pesquisador_sistema text not null default '',
  pesquisador text not null default '',
  data_inicio_coleta text not null default '',
  data_fim_coleta text not null default '',
  linha_origem text not null default '',
  data_execucao_carga text not null default '',
  data_hora_execucao_carga text not null default '',
  sync_run_id text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_empetur_tabela_base_origem unique (codigo_pesquisa, nro_identificacao)
);

create or replace function public.set_empetur_tabela_base_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_empetur_tabela_base_updated_at on public.empetur_tabela_base;

create trigger trg_empetur_tabela_base_updated_at
before update on public.empetur_tabela_base
for each row
execute function public.set_empetur_tabela_base_updated_at();

create index if not exists idx_empetur_tabela_base_codigo_pesquisa
on public.empetur_tabela_base (codigo_pesquisa);

create index if not exists idx_empetur_tabela_base_municipio
on public.empetur_tabela_base (municipio);

create index if not exists idx_empetur_tabela_base_questionario
on public.empetur_tabela_base (questionario_preenchido);
