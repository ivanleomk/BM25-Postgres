CREATE EXTENSION vector;
CREATE EXTENSION pg_search;

CREATE TABLE chunk (
    id SERIAL,
    context TEXT,
    repo VARCHAR(255),
    vector vector(1536),
    text TEXT,
    issue_id INTEGER,
    issue_number INTEGER,
    chunk_id TEXT,
    timestamp TIMESTAMP
);

-- This create a BM25 search index on the chunk table
CALL paradedb.create_bm25(
        index_name => 'search_idx',
        schema_name => 'public',
        table_name => 'chunk',
        key_field => 'id',
        text_fields => '{text: {tokenizer: {type: "en_stem"}}, context: {}}',
        numeric_fields => '{issue_id: {},issue_number:{}}'
);

CREATE INDEX ON public.chunk
USING hnsw (vector vector_cosine_ops);