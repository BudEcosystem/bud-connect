# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BudConnect is a cloud service that complements and manages Bud inference runtimes deployed on customer infrastructure. It serves as a central registry and sync point for:
- Compatibility validation of models and engine versions
- Regular updates for engine versions, leaderboards, and other resources
- Hardware information and cost management

## Tech Stack

- **Python 3.8+** with FastAPI for REST APIs
- **SQLAlchemy 2.0+** ORM with PostgreSQL database
- **Alembic** for database migrations
- **Dapr** for distributed microservices runtime
- **Redis** for caching and distributed operations
- **Docker & Kubernetes** with Helm charts for deployment
- **BudMicroframe** - Internal Bud Ecosystem microservices framework

## Development Commands

### Starting Development Environment
```bash
# Set up environment variables
cp .env.sample .env

# Start all services (PostgreSQL, Redis, Dapr, and the app)
./deploy/start_dev.sh

# Start with rebuild
./deploy/start_dev.sh --build

# Start in detached mode
./deploy/start_dev.sh -d

# Stop services
./deploy/stop_dev.sh
```

### Database Migrations
```bash
# Generate new migration
docker exec -it budserve-<namespace>-budconnect alembic -c ./alembic.ini revision --autogenerate -m "description"

# Apply migrations
docker exec -it budserve-<namespace>-budconnect alembic -c ./alembic.ini upgrade head
```

### Code Quality
```bash
# Run linter
ruff check .

# Fix linting issues
ruff check . --fix

# Format code
ruff format .

# Type checking
mypy budconnect/
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_specific.py

# Run with coverage
pytest --cov=budconnect
```

## Architecture

The project follows a modular microservices architecture:

### Core Modules
- **Engine Module** (`budconnect/modules/engine/`): Manages engine versions and model compatibilities
- **Model Module** (`budconnect/modules/model/`): Handles model information, licenses, and resources
- **Hardware Module** (`budconnect/modules/hardware/`): Manages hardware information and costs
- **Leaderboard Module** (`budconnect/modules/leaderboard/`): Manages performance leaderboards
- **Provider Module** (`budconnect/modules/provider/`): Handles external providers (litellm, tensorzero)

### Key Components
- **Seeders** (`budconnect/seeders/`): Automated data population for engines, models, and providers
- **Workflows** (`budconnect/workflows/`): Dapr workflow implementations
- **Base Classes** (`budconnect/base/`): Base controller, service, and repository classes using BudMicroframe

### Database Models
All SQLAlchemy models are in `budconnect/models/` with relationships between:
- Engines ↔ Models (many-to-many via EngineModelCompatibility)
- Providers → Engines
- Models → Hardware requirements
- Leaderboards → Models

## Code Style

- **Line length**: 119 characters max
- **Docstring format**: Google style
- **Import sorting**: Managed by Ruff with 2 blank lines after imports
- **Type hints**: Required for all functions (enforced by MyPy)
- **Async/await**: Used throughout for database operations and API endpoints

## Development Workflow

1. Work on feature branches (e.g., `feature/tensorzero`)
2. Main branch is `main` for PRs
3. The app auto-reloads on code changes when using `./deploy/start_dev.sh`
4. Dapr components are configured in `.dapr/components/`
5. Environment variables are loaded from `.env` file

## Current Work

The `feature/tensorzero` branch is adding support for TensorZero provider with:
- New seeder data in `budconnect/seeders/data/tensorzero/`
- tensorzero seeder implementation in `budconnect/seeders/tensorzero.py`
- Updated engine configurations in `budconnect/seeders/data/engines.json`

## Important Notes

- Always run migrations after pulling changes
- The service uses Dapr for service-to-service communication
- All API endpoints follow RESTful conventions with Pydantic models
- Hardware architectures supported: CUDA, CPU, ROCM, HPU
- Engine versions follow Bud release versioning, not upstream project versions