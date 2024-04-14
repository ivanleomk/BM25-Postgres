start:
	docker run --name pg -p 5432:5432 --env-file .env pg-db 

clean:
	docker build --no-cache -t pg-db -f ./Docker/Dockerfile 

build:
	docker build -t pg-db -f ./Docker/Dockerfile .

teardown:
	docker rm -f pg || true

restart: teardown build start

clean-build: teardown clean start
