# Introduction

This is a repository that aims to show how to use `pg_search` from `parade_db` to run a simple BM25 search for a given query. 

Goals

- [x] Install pg_search and pgvector
  - [x] Create docker image for use
  - [x] Create a search index based off the text and context columns
  - [x] Create a HSNW index for vectors
- [x] Ingest data from the issues database
- [x] Queries
  - [x] Run a query using keywords
  - [x] Implement naive unigram and bigram matching of queries
  - [x] ~~Run a query using a phrase~~ ( Not possible with pg_search )
  - [x] Run a query using a vector
  - [ ] Run a query using hybrid search
  - [ ] Run a query using cohere's re-rankers
- [ ] Synthethic Data
  - [ ] Generate Synthethic Data for each individual comment that we have
- [ ] Evals
  - [ ] Evaluate using MRR
  - [ ] Evaluate using MAR

## Installation Instructions

> Please create a `.env` file before starting to work with this repository. You'll need the following
> ```
> POSTGRES_USER=postgres
> POSTGRES_PASSWORD=password
> POSTGRES_DB=testdatabase
> ```

There's a makefile to work with Docker easily. To boot up our postgres database image, just run the commands

```
make build 
make start
```

There are a few other docker commands
- `clean-build` : This rebuilds the docker image without using the cache and then starts it up
- `restart` : This deletes the `pg` docker container and restarts it from scratch

To verify that the database is working and accepting queries, you can run `python3 test.py` which will test the database port and connection.

## Testing Queries

> Make sure to install the required libraries in a virtual environment before proceeding

We'll be using the `bigcode/the-stack-github-issues` to generate some data that we can use to benchmark semantic, bm25 and subsequently how a re-ranker changes things.

You can interact with the database with 

```
docker exec -it pg psql -U <username> -d <databasename>
```

To insert issues into your database, just run the `scripts/insert.py`, this will pull the first 300 issues that are tagged as either `pytorch` or `react` from the database and embed them so that we can query them down the line.

Once you've ingested the data, you can then query the database using the `query.py` file which supports querying our database using keywords
