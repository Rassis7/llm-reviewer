docker-up:
	docker compose up

docker-down:
	docker compose down

docker-build:
	docker compose build && docker compose up