# Copilot Instructions for minigrid-backend

## Project Overview
This is a Python backend project organized as a FastAPI application. The codebase is structured into clear domains: models, schemas, and routers, each grouped by business entity (e.g., `minigrid`, `site`, `utilisateur`).

## Architecture & Patterns
- **app/main.py**: Entry point for the FastAPI app. Routers are registered here.
- **app/models/**: SQLAlchemy ORM models for each business entity. Each file defines a single entity (e.g., `minigrid.py`, `site.py`).
- **app/schemas/**: Pydantic schemas for request/response validation, mirroring the models structure.
- **app/routers/**: FastAPI routers for each entity, handling API endpoints. Each router imports its model and schema.
- **app/db.py**: Database connection and session management.

### Example Pattern
For a new entity (e.g., `equipement_type`):
- Model: `app/models/equipement_type.py`
- Schema: `app/schemas/equipement_type.py`
- Router: `app/routers/equipement_type.py`

## Developer Workflows
- **Run the app**: Typically via `uvicorn app.main:app --reload` from the project root.
- **Dependencies**: Managed in `requirements.txt`. Install with `pip install -r requirements.txt`.
- **Database**: SQLAlchemy is used. DB config is in `app/db.py`.
- **Testing**: No explicit test directory found; add tests under `tests/` if needed.

## Project Conventions
- Each business entity has a dedicated model, schema, and router file.
- File and class names are in French, matching the business domain.
- Avoid mixing logic between routers, models, and schemas—keep layers separate.
- Use Pydantic schemas for all request/response validation.

## Integration Points
- The app is modular: routers are registered in `main.py`.
- All DB access is via SQLAlchemy models in `app/models/`.
- External dependencies are listed in `requirements.txt`.

## Key Files
- `app/main.py`: App entry, router registration
- `app/db.py`: DB session setup
- `app/models/`, `app/schemas/`, `app/routers/`: Core business logic, validation, and API

---

**For AI agents:**
- Follow the established model/schema/router pattern for new features.
- Use French naming conventions for new business entities.
- Register new routers in `main.py`.
- Keep business logic out of routers—use models for DB logic, schemas for validation.
