start:
	docker run --name pg -p 5432:5432 pg-db

clean:
	docker build --no-cache -t pg-db .

build:
	docker build -t pg-db .

restart:
	docker rm -f pg && $(MAKE) start

test:
	$(MAKE) clean && $(MAKE) restart