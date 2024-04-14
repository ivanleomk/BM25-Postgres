CREATE EXTENSION vector;
CREATE EXTENSION pg_search;

CREATE TABLE chunk (
    id SERIAL,
    context TEXT,
    repo VARCHAR(255),
    vector vector(1256),
    text TEXT,
    issue_id INTEGER,
    issue_number INTEGER,
    timestamp TIMESTAMP
);
