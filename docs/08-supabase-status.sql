create table if not exists public.empetur_municipios_status (
  municipio_slug text primary key,
  concluido boolean not null default false,
  updated_at timestamptz not null default now()
);

create or replace function public.set_empetur_municipios_status_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_empetur_municipios_status_updated_at on public.empetur_municipios_status;

create trigger trg_empetur_municipios_status_updated_at
before update on public.empetur_municipios_status
for each row
execute function public.set_empetur_municipios_status_updated_at();
