create table public.artifacts (
  artifact_id text not null,
  tenant_id uuid not null,
  session_id uuid null,
  solution_id uuid null,
  execution_id text null,
  artifact_type text not null,
  realm text null,
  lifecycle_state text not null default 'draft'::text,
  owner text not null default 'client'::text,
  purpose text not null default 'delivery'::text,
  lifecycle_transitions jsonb null default '[]'::jsonb,
  payload_storage_path text null,
  payload_artifact_id text null,
  metadata jsonb null default '{}'::jsonb,
  regenerable boolean null default true,
  retention_policy text null default 'session'::text,
  intent_type text null,
  intent_id text null,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  version integer null default 1,
  parent_artifact_id text null,
  is_current_version boolean null default true,
  source_artifact_ids jsonb null default '[]'::jsonb,
  constraint artifacts_pkey primary key (artifact_id),
  constraint artifacts_lifecycle_state_check check (
    (
      lifecycle_state = any (
        array['draft'::text, 'accepted'::text, 'obsolete'::text]
      )
    )
  ),
  constraint artifacts_owner_check check (
    (
      owner = any (
        array['client'::text, 'platform'::text, 'shared'::text]
      )
    )
  ),
  constraint artifacts_purpose_check check (
    (
      purpose = any (
        array[
          'decision_support'::text,
          'delivery'::text,
          'governance'::text,
          'learning'::text
        ]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_artifacts_source_artifact_ids on public.artifacts using gin (source_artifact_ids) TABLESPACE pg_default;

create index IF not exists idx_artifacts_dependencies_tenant on public.artifacts using btree (tenant_id, source_artifact_ids) TABLESPACE pg_default
where
  (jsonb_array_length(source_artifact_ids) > 0);

create index IF not exists idx_artifacts_tenant_id on public.artifacts using btree (tenant_id) TABLESPACE pg_default;

create index IF not exists idx_artifacts_session_id on public.artifacts using btree (session_id) TABLESPACE pg_default;

create index IF not exists idx_artifacts_solution_id on public.artifacts using btree (solution_id) TABLESPACE pg_default;

create index IF not exists idx_artifacts_execution_id on public.artifacts using btree (execution_id) TABLESPACE pg_default;

create index IF not exists idx_artifacts_artifact_type on public.artifacts using btree (artifact_type) TABLESPACE pg_default;

create index IF not exists idx_artifacts_realm on public.artifacts using btree (realm) TABLESPACE pg_default;

create index IF not exists idx_artifacts_lifecycle_state on public.artifacts using btree (lifecycle_state) TABLESPACE pg_default;

create index IF not exists idx_artifacts_owner on public.artifacts using btree (owner) TABLESPACE pg_default;

create index IF not exists idx_artifacts_purpose on public.artifacts using btree (purpose) TABLESPACE pg_default;

create index IF not exists idx_artifacts_created_at on public.artifacts using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists idx_artifacts_tenant_lifecycle on public.artifacts using btree (tenant_id, lifecycle_state) TABLESPACE pg_default;

create index IF not exists idx_artifacts_tenant_type on public.artifacts using btree (tenant_id, artifact_type) TABLESPACE pg_default;

create index IF not exists idx_artifacts_session_type on public.artifacts using btree (session_id, artifact_type) TABLESPACE pg_default
where
  (session_id is not null);

create index IF not exists idx_artifacts_lifecycle_owner on public.artifacts using btree (lifecycle_state, owner) TABLESPACE pg_default;

create index IF not exists idx_artifacts_parent_artifact_id on public.artifacts using btree (parent_artifact_id) TABLESPACE pg_default
where
  (parent_artifact_id is not null);

create index IF not exists idx_artifacts_version on public.artifacts using btree (version) TABLESPACE pg_default;

create index IF not exists idx_artifacts_is_current_version on public.artifacts using btree (is_current_version) TABLESPACE pg_default
where
  (is_current_version = true);

create index IF not exists idx_artifacts_version_chain on public.artifacts using btree (parent_artifact_id, version, is_current_version) TABLESPACE pg_default;

create index IF not exists idx_artifacts_current_version_tenant_type on public.artifacts using btree (tenant_id, artifact_type, is_current_version) TABLESPACE pg_default
where
  (is_current_version = true);

create trigger update_artifacts_updated_at BEFORE
update on artifacts for EACH row
execute FUNCTION update_artifacts_updated_at ();