# Data Model: Integrated RAG Chatbot for Docusaurus Book

## Overview
This document describes the data structures and entities for the RAG chatbot system, including both the vector database (Qdrant) and relational database (Neon Postgres) components.

## Entity: Content Chunk (Qdrant Collection)

### Schema Definition
```python
# Qdrant Collection: book_content_chunks
{
  "payload": {
    "content_id": str,           # Unique identifier for the content chunk
    "book_id": str,              # Identifier for the book this chunk belongs to
    "title": str,                # Title of the section/chapter
    "section": str,              # Section name or hierarchy
    "page_number": int,          # Page number if applicable
    "chunk_index": int,          # Position of this chunk within the document
    "original_text": str,        # The original text content (truncated if needed)
    "source_file": str,          # Source file path
    "created_at": str,           # Timestamp of creation
    "metadata": dict             # Additional metadata (authors, tags, etc.)
  },
  "vector": list[float]          # Embedding vector
}
```

### Validation Rules
- `content_id` must be unique within the collection
- `original_text` maximum length: 4000 characters
- `vector` must have consistent dimension (384 for all-MiniLM-L6-v2)

## Entity: User Query Session (Neon Postgres)

### Table Definition
```sql
-- Table: user_query_sessions
CREATE TABLE user_query_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255),           -- Anonymous session identifier
    user_id UUID,                         -- For authenticated users (optional)
    question TEXT NOT NULL,               -- User's original question
    context_type VARCHAR(20) NOT NULL,    -- 'full_book', 'chapter', 'selection'
    selected_text TEXT,                   -- Text selected by user (if applicable)
    retrieved_chunks JSONB,               -- Retrieved context chunks with scores
    answer TEXT NOT NULL,                 -- AI-generated answer
    citations JSONB,                      -- Source citations for the answer
    response_time_ms INTEGER,             -- Time taken to generate response
    created_at TIMESTAMP DEFAULT NOW(),   -- Timestamp of query
    updated_at TIMESTAMP DEFAULT NOW()    -- Timestamp of last update
);
```

### Validation Rules
- `question` length: 10-2000 characters
- `context_type` must be one of: 'full_book', 'chapter', 'selection'
- `selected_text` length: maximum 5000 characters (as per requirement)
- `response_time_ms` must be positive

## Entity: Book Metadata (Neon Postgres)

### Table Definition
```sql
-- Table: book_metadata
CREATE TABLE book_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    author VARCHAR(250),
    description TEXT,
    version VARCHAR(20),
    total_chunks INTEGER DEFAULT 0,
    total_pages INTEGER,
    word_count INTEGER,
    ingestion_status VARCHAR(20) DEFAULT 'pending',  -- pending, in_progress, completed, failed
    ingestion_started_at TIMESTAMP,
    ingestion_completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Validation Rules
- `title` required, maximum 500 characters
- `ingestion_status` must be one of: 'pending', 'in_progress', 'completed', 'failed'
- `total_chunks`, `total_pages`, `word_count` must be non-negative

## Entity: Content Embedding Record (Neon Postgres)

### Table Definition
```sql
-- Table: content_embeddings
CREATE TABLE content_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id VARCHAR(255) NOT NULL,     -- Matches Qdrant payload content_id
    book_id UUID NOT NULL,
    chunk_text TEXT NOT NULL,             -- Original text chunk
    chunk_title VARCHAR(500),
    chunk_section VARCHAR(200),
    chunk_index INTEGER NOT NULL,
    source_file VARCHAR(500),
    embedding_status VARCHAR(20) DEFAULT 'pending',  -- pending, processed, failed
    vector_id VARCHAR(255),               -- Qdrant point ID
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (book_id) REFERENCES book_metadata(id)
);
```

### Validation Rules
- `content_id` must be unique
- `embedding_status` must be one of: 'pending', 'processed', 'failed'
- `chunk_index` must be non-negative

## Entity: User Session (Neon Postgres)

### Table Definition
```sql
-- Table: user_sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE NOT NULL,  -- Anonymous session identifier
    is_authenticated BOOLEAN DEFAULT FALSE,
    user_id UUID,                                  -- For authenticated users
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

### Validation Rules
- `session_token` must be unique
- `expires_at` must be in the future

## Entity: API Usage Metrics (Neon Postgres)

### Table Definition
```sql
-- Table: api_usage_metrics
CREATE TABLE api_usage_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255),           -- Anonymous session identifier
    endpoint VARCHAR(100) NOT NULL,       -- API endpoint called
    request_data JSONB,                   -- Request payload (anonymized)
    response_time_ms INTEGER,             -- Response time in milliseconds
    status_code INTEGER,                  -- HTTP status code
    rate_limited BOOLEAN DEFAULT FALSE,   -- Whether request was rate limited
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Validation Rules
- `endpoint` must be one of: '/query', '/query/selection', '/ingest', '/health'
- `response_time_ms` must be positive
- `status_code` must be valid HTTP status code

## Relationships

### Between Book Metadata and Content Embeddings
- `book_metadata.id` → `content_embeddings.book_id` (one-to-many)

### Between User Sessions and Query Sessions
- `user_sessions.session_token` → `user_query_sessions.session_token` (one-to-many)

### Between Book Metadata and Query Sessions
- `book_metadata.id` → `user_query_sessions.book_id` (many-to-one, via book context)

## State Transitions

### Content Ingestion Process
1. `pending` → `in_progress` when ingestion starts
2. `in_progress` → `completed` when all chunks processed successfully
3. `in_progress` → `failed` when errors occur during ingestion
4. `failed` → `pending` when retry is initiated

### Query Session States
- Created when user submits question
- Updated when response is generated
- Archived based on retention policy