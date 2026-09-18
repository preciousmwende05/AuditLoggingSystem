.PHONY: up down logs backend-shell frontend-shell test lint fmt migrate

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

backend-shell:
	docker compose exec backend sh

frontend-shell:
	docker compose exec frontend sh

test:
	cd backend && . .venv/bin/activate && pytest -q

lint:
	cd backend && . .venv/bin/activate && ruff check app tests
	cd frontend && npm run lint

fmt:
	cd backend && . .venv/bin/activate && isort app tests && black app tests
	cd frontend && npx prettier --write "src/**/*.{ts,tsx}"

migrate:
	docker compose exec backend alembic upgrade head
