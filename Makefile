.PHONY: up down rebuild logs seed reset

up:
	docker-compose up --build

down:
	docker-compose down

rebuild:
	docker-compose down
	docker-compose up --build

logs:
	docker-compose logs -f --tail=200

seed:
	docker-compose exec backend python -m app.seed_demo

reset:
	docker-compose down -v
