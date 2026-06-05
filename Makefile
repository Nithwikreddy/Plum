.PHONY: help dev test test-watch seed clean docker-build docker-up docker-down install

help:
	@echo "OPD Claim Adjudication MVP - Commands"
	@echo "====================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start development servers (local Python/Node)"
	@echo "  make install          - Install dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-watch       - Run tests in watch mode"
	@echo ""
	@echo "Database:"
	@echo "  make seed             - Seed test data"
	@echo "  make migrate          - Run database migrations"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Clean up temporary files"
	@echo ""

install:
	@echo "Installing dependencies..."
	cd apps/api && pip install -r requirements.txt
	cd apps/web && npm install

dev:
	@echo "Starting development servers..."
	@echo ""
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo ""
	@echo "In separate terminals:"
	@echo "  Terminal 1: cd apps/api && python wsgi.py"
	@echo "  Terminal 2: cd apps/web && npm run dev"
	@echo ""

test:
	@echo "Running tests..."
	cd apps/api && pytest tests/ -v

test-watch:
	@echo "Running tests in watch mode..."
	cd apps/api && pytest tests/ -v --tb=short -s

test-docker:
	@echo "Running tests inside Docker container..."
	@docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@docker compose -f docker-compose.test.yml down --volumes

seed:
	@echo "Seeding database..."
	cd apps/api && python -c "from app.main import create_app; app = create_app(); print('Database seeded with test members')"

migrate:
	@echo "Running migrations..."
	cd apps/api && flask db upgrade

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo ""
	@echo "Waiting for services to start..."
	@sleep 5
	@echo ""
	@echo "Services running:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Health: http://localhost:8000/health"
	@echo "  Database: localhost:5432 (opd_user/opd_password)"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-logs-api:
	docker-compose logs -f api

docker-logs-web:
	docker-compose logs -f web

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf apps/web/.next apps/web/.turbo apps/web/node_modules
	rm -rf apps/api/.env.local
	@echo "Cleanup complete"
