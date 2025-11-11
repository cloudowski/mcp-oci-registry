APP_MODULE ?= server:asgi_app
HOST ?= 127.0.0.1
PORT ?= 8888
IMAGE ?= mcp-oci-registry

.PHONY: install run docker-build docker-run compose-up compose-down compose-logs test

install:
	pip install -r requirements.txt

run:
	uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)

docker-build:
	docker build -t $(IMAGE) .

docker-run: docker-build
	docker run --rm -p $(PORT):8000 $(IMAGE)

compose-up:
	docker compose up --build

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f

test:
	pytest -v


