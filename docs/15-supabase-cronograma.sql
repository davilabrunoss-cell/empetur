create table if not exists public.empetur_cronograma (
  municipio_slug text not null,
  codigo text not null,
  data_visita date,
  updated_at timestamptz not null default now(),
  primary key (municipio_slug, codigo),
  constraint empetur_cronograma_codigo_check
    check (codigo ~ '^(A[0-9]+(\.[0-9]+)?|B[0-9]+|C[0-9]+)-[0-9]{4}$')
);

create table if not exists public.empetur_cronograma_edit_tokens (
  municipio_slug text primary key,
  token_hash text not null check (token_hash ~ '^[0-9a-f]{64}$'),
  updated_at timestamptz not null default now()
);

alter table public.empetur_cronograma enable row level security;
alter table public.empetur_cronograma_edit_tokens enable row level security;

revoke all on table public.empetur_cronograma from anon, authenticated;
revoke all on table public.empetur_cronograma_edit_tokens from anon, authenticated;

grant select, insert, update on table public.empetur_cronograma to service_role;
grant select on table public.empetur_cronograma_edit_tokens to service_role;
