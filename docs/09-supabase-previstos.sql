create table if not exists public.empetur_previstos_atrativos (
  id bigint generated always as identity primary key,
  municipio_slug text not null,
  regiao text not null default '',
  municipio text not null default '',
  categoria text not null default '',
  referencia text not null default '',
  atrativo text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create or replace function public.set_empetur_previstos_atrativos_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_empetur_previstos_atrativos_updated_at on public.empetur_previstos_atrativos;

create trigger trg_empetur_previstos_atrativos_updated_at
before update on public.empetur_previstos_atrativos
for each row
execute function public.set_empetur_previstos_atrativos_updated_at();

create index if not exists idx_empetur_previstos_atrativos_municipio_slug
on public.empetur_previstos_atrativos (municipio_slug);
