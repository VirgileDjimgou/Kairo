# Data Model Specification

## 1. Common Columns

Most tenant-scoped tables should include:

```text
id UUID primary key
tenant_id UUID not null
created_at timestamptz not null
updated_at timestamptz not null
deleted_at timestamptz null
created_by UUID null
updated_by UUID null
version integer not null default 1
metadata jsonb not null default '{}'
```

## 2. Identity Tables

### tenants

```text
id
slug
name
type
status
default_language
branding_json
settings_json
created_at
updated_at
```

### users

```text
id
email
password_hash
display_name
status
last_login_at
created_at
updated_at
```

### tenant_users

```text
id
tenant_id
user_id
membership_status
profile_type
joined_at
created_at
updated_at
```

### roles

```text
id
tenant_id
code
name
description
is_system_role
```

### permissions

```text
id
code
description
```

### role_permissions

```text
role_id
permission_id
```

### user_roles

```text
tenant_user_id
role_id
```

## 3. Document Tables

### documents

```text
id
tenant_id
title
description
source_type
language
access_scope
owner_user_id null
status
current_version_id
created_by
created_at
updated_at
```

### document_versions

```text
id
tenant_id
document_id
version_number
file_name
mime_type
file_size_bytes
storage_bucket
storage_key
checksum
created_by
created_at
```

### document_allowed_roles

```text
document_id
role_id
```

### ingestion_jobs

```text
id
tenant_id
document_id
document_version_id
status
error_message
started_at
finished_at
created_at
```

### document_chunks

```text
id
tenant_id
document_id
document_version_id
chunk_index
text
language
token_count
qdrant_point_id
metadata
created_at
```

## 4. Chat Tables

### conversations

```text
id
tenant_id
user_id
title
status
created_at
updated_at
```

### messages

```text
id
tenant_id
conversation_id
user_id null
role
content
created_at
metadata
```

### answer_citations

```text
id
tenant_id
message_id
document_id
document_version_id
chunk_id
quote_excerpt
score
created_at
```

## 5. Business Tables

### membership_profiles

```text
id
tenant_id
user_id null
member_code
first_name
last_name
display_name
email
phone
status
joined_at
metadata
```

### contribution_records

```text
id
tenant_id
membership_profile_id
year
expected_amount
paid_amount
balance
currency
status
due_date
metadata
```

### payment_records

```text
id
tenant_id
contribution_record_id
amount
currency
paid_at
payment_method
reference
recorded_by
metadata
```

### events

```text
id
tenant_id
title
description
start_at
end_at
location
visibility_scope
status
created_by
metadata
```

### announcements

```text
id
tenant_id
title
body
visibility_scope
published_at
expires_at
created_by
metadata
```

### policy_records

```text
id
tenant_id
title
category
description
document_id null
status
created_by
metadata
```

### disciplinary_records

```text
id
tenant_id
membership_profile_id
policy_record_id null
title
description
amount
currency
status
recorded_by
recorded_at
metadata
```

## 6. Audit Tables

### audit_logs

```text
id
tenant_id
actor_user_id
action
resource_type
resource_id
ip_address
user_agent
correlation_id
metadata
created_at
```

## 7. Qdrant Payload Standard

Every vector point payload must contain:

```json
{
  "tenant_id": "uuid",
  "document_id": "uuid",
  "document_version_id": "uuid",
  "chunk_id": "uuid",
  "access_scope": "tenant_public",
  "owner_user_id": null,
  "allowed_role_ids": [],
  "language": "fr",
  "source_type": "pdf",
  "created_at": "2026-01-01T00:00:00Z"
}
```
