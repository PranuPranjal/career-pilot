# CareerPilot AI — Phase 1 implementation

Phase 1 provides the development foundation and first candidate onboarding vertical slice:
- FastAPI API with PostgreSQL support and SQLite local fallback
- Tenant and user registration/login
- Password hashing and JWT access tokens
- Tenant-scoped candidate profiles
- Private resume upload (PDF/DOCX), text extraction and basic evidence extraction
- Candidate facts with `proposed`, `confirmed` and `rejected` states
- Conversational onboarding starter that asks about missing profile information
- Next.js frontend starter with register/login and dashboard flow
- Docker Compose for PostgreSQL and Redis
- CI workflow, Alembic migration setup and environment template

## Run locally with Docker
1. Copy `.env.example` to `.env` and replace `JWT_SECRET_KEY`.
2. Run `docker compose up --build`.
3. API docs: http://localhost:8000/docs
4. Web: http://localhost:3000

## Run API without Docker
```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp ../../.env.example ../../.env
uvicorn app.main:app --reload
```

## Run web without Docker
```bash
cd apps/web
npm install
npm run dev
```
Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `apps/web/.env.local`.

## API flow
1. `POST /api/v1/auth/register`
2. `POST /api/v1/auth/login`
3. Use the returned bearer token in Swagger's Authorize dialog.
4. `GET /api/v1/me`
5. `POST /api/v1/resumes` (multipart field: `file`)
6. `GET /api/v1/profile`
7. `GET /api/v1/profile/facts`
8. `POST /api/v1/profile/facts/{fact_id}/confirm`
9. `POST /api/v1/onboarding/messages`

## Important limitations
- Resume extraction is a starter parser, not a production-grade resume understanding model.
- The onboarding assistant currently uses deterministic prompts. Add a provider-neutral LLM service only after data-processing consent, provider retention and privacy review.
- This phase does not yet include email verification, password reset, MFA, antivirus scanning, cloud object storage, production secrets management, complete DPDP workflows or a formal security audit.
- The local file store is for development only. Use private object storage and malware scanning before production.
- JWT tokens are short-lived; refresh-token rotation and session revocation are a later hardening task.
- Do not expose this starter to public users with real resumes before the remaining security controls are completed.

## Architecture
- `apps/api`: FastAPI modular monolith
- `apps/web`: Next.js App Router
- `infra`: Docker and database configuration
- `docs`: phase requirements and architecture notes


## Resume upload fix

If you downloaded the original Phase 1 starter before this fix, replace
`apps/api/app/routers/resumes.py` with the file in this package, then rebuild
the API container. The upload handler now flushes the `Resume` row before
inserting related `CandidateFact` rows and rolls back the database transaction
and removes the uploaded file if saving fails.


## Phase 2: Job discovery

See [docs/PHASE2.md](docs/PHASE2.md) for supported public job boards, source registration, sync, search endpoints, and migration instructions.
