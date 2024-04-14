## Installation Instructions

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

We'll be using the `bigcode/the-stack-github-issues` 