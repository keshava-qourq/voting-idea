# Data Model

<!-- sdlc:auto:start entities -->
### users

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| email | varchar(254) UNIQUE, stored lower-cased | False | — | False |
| password_hash | varchar(255) | False | — | False |
| created_at | timestamptz | False | — | False |

### sessions

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| user_id | uuid | False | users.id | False |
| token_hash | char(64) UNIQUE (SHA-256 of the opaque token) | False | — | False |
| created_at | timestamptz | False | — | False |
| expires_at | timestamptz | False | — | False |
| revoked_at | timestamptz | False | — | True |

### ideas

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| user_id | uuid | False | users.id | False |
| title | varchar(120) | False | — | False |
| description | varchar(500) | False | — | False |
| created_at | timestamptz | False | — | False |

### votes

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | uuid | True | — | False |
| user_id | uuid | False | users.id | False |
| idea_id | uuid | False | ideas.id | False |
| created_at | timestamptz | False | — | False |
<!-- sdlc:auto:end entities -->

<!-- sdlc:auto:start relationships -->
| Source | Target | Type |
|---|---|---|
| users | sessions | one-to-many |
| users | ideas | one-to-many |
| users | votes | one-to-many |
| ideas | votes | one-to-many |
<!-- sdlc:auto:end relationships -->

<!-- sdlc:auto:start er-diagram -->
```mermaid
erDiagram
  users {
    uuid id PK
    varchar_254__UNIQUE__stored_lower_cased email
    varchar_255_ password_hash
    timestamptz created_at
  }
  sessions {
    uuid id PK
    uuid user_id FK
    char_64__UNIQUE__SHA_256_of_the_opaque_token_ token_hash
    timestamptz created_at
    timestamptz expires_at
    timestamptz revoked_at
  }
  ideas {
    uuid id PK
    uuid user_id FK
    varchar_120_ title
    varchar_500_ description
    timestamptz created_at
  }
  votes {
    uuid id PK
    uuid user_id FK
    uuid idea_id FK
    timestamptz created_at
  }
  users ||--o{ sessions : "one-to-many"
  users ||--o{ ideas : "one-to-many"
  users ||--o{ votes : "one-to-many"
  ideas ||--o{ votes : "one-to-many"
```
<!-- sdlc:auto:end er-diagram -->
