create or replace function public.get_kalatrace_infrastructure_usage()
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public, storage
as $$
declare
  db_bytes bigint;
  storage_bytes bigint;
  storage_objects bigint;
  db_quota_bytes bigint := 500 * 1024 * 1024;
  storage_quota_bytes bigint := 1 * 1024 * 1024 * 1024;
  bucket_rows jsonb;
begin
  if auth.uid() is null then
    raise exception 'authentication required';
  end if;

  select pg_database_size(current_database()) into db_bytes;

  select
    coalesce(sum(coalesce((metadata->>'size')::bigint, 0)), 0),
    count(*)
  into storage_bytes, storage_objects
  from storage.objects;

  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'bucket_id', bucket_id,
        'bytes', total_bytes,
        'objects', object_count
      )
      order by total_bytes desc
    ),
    '[]'::jsonb
  )
  into bucket_rows
  from (
    select
      bucket_id,
      coalesce(sum(coalesce((metadata->>'size')::bigint, 0)), 0) as total_bytes,
      count(*) as object_count
    from storage.objects
    group by bucket_id
  ) buckets;

  return jsonb_build_object(
    'project', 'Kalatrace',
    'database', jsonb_build_object(
      'bytes', db_bytes,
      'quota_bytes', db_quota_bytes,
      'available_bytes', greatest(db_quota_bytes - db_bytes, 0),
      'usage_percent', round((db_bytes::numeric / db_quota_bytes) * 100, 2),
      'status', case
        when db_bytes >= db_quota_bytes then 'critical'
        when db_bytes >= db_quota_bytes * 0.9 then 'warning'
        else 'healthy'
      end
    ),
    'storage', jsonb_build_object(
      'bytes', storage_bytes,
      'quota_bytes', storage_quota_bytes,
      'available_bytes', greatest(storage_quota_bytes - storage_bytes, 0),
      'usage_percent', round((storage_bytes::numeric / storage_quota_bytes) * 100, 2),
      'objects', storage_objects,
      'status', case
        when storage_bytes >= storage_quota_bytes then 'critical'
        when storage_bytes >= storage_quota_bytes * 0.9 then 'warning'
        else 'healthy'
      end,
      'buckets', bucket_rows
    ),
    'database_name', current_database(),
    'measured_at', now()
  );
end;
$$;

revoke all on function public.get_kalatrace_infrastructure_usage() from public;
revoke all on function public.get_kalatrace_infrastructure_usage() from anon;
grant execute on function public.get_kalatrace_infrastructure_usage() to authenticated;
