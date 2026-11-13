# CareerPilot Phase 2 — Job sources, ingestion and discovery

## Delivered in this starter

- Common adapter contract and normalized job representation.
- Public listing adapters for Greenhouse Job Board API, Lever Postings API and Ashby Job Postings API.
- Shared source registry and normalized job-posting tables.
- Manual source registration and sync endpoints.
- Upsert/deduplication by `(source_id, external_id)`.
- Content hashes and first/last-seen timestamps.
- Jobs absent from a successful non-empty source refresh are marked `stale`; an empty feed does not mass-expire existing listings.
- Search by title, company, department, description and location, with provider/employment/workplace filters and pagination.
- Basic job-source and job-search UI in the Next.js workspace.

## Public source identifiers

- Greenhouse: `board_token` is the token in `https://boards.greenhouse.io/{board_token}`.
- Lever: `board_token` is the site name in `https://jobs.lever.co/{site_name}`.
- Ashby: `board_token` is the final path segment in `https://jobs.ashbyhq.com/{job_board_name}`.

Only add job boards that are publicly available and whose use is permitted. A board token is an identifier, not an authorization credential. The implementation makes requests only to the providers' documented public listing endpoints; it does not crawl arbitrary URLs.

## API

All endpoints require the Phase 1 bearer token.

- `GET /api/v1/sources`
- `POST /api/v1/sources` with `{ "provider": "greenhouse|lever|ashby", "company_name": "Example Co", "board_token": "example" }`
- `POST /api/v1/sources/{source_id}/sync`
- `GET /api/v1/jobs?q=engineer&location=India&provider=greenhouse&page=1&page_size=20`
- `GET /api/v1/jobs/{job_id}`

A successful sync returns counts for fetched, created, updated and marked-stale records. A failed sync records a failure status and short error message on the source.

## Apply the Phase 2 database migration

The API container already runs `alembic upgrade head` at startup. Rebuild/recreate the API container from the project root:

```powershell
docker compose up -d --build api
```

Check migration and API logs:

```powershell
docker compose logs --tail=100 api
```

Do not run `docker compose down -v`; that deletes the PostgreSQL volume and your Phase 1 user/resume data.

## Run the app

```powershell
docker compose up -d --build
```

Open `http://localhost:3000`, sign in, add a public board, click **Sync now**, then search jobs. API documentation is at `http://localhost:8000/docs`.

## Current limitations / next implementation steps

- Sync is initiated manually and runs in the API request. A Redis-backed worker, retry policy, scheduled refresh cadence and per-provider rate limiting are the next reliability increment.
- Greenhouse and Lever company names are taken from the source registry when the public payload does not include one. Ashby likewise uses the configured company name.
- The current UI accepts board tokens manually; it does not yet discover boards automatically from arbitrary company career pages or social posts.
- Cross-source semantic deduplication is not enabled yet. Exact source-record duplicates are prevented; likely duplicate roles across separate boards need a later matching layer.
- Search is PostgreSQL `ILIKE` based. Ranking, facets, saved searches and personalized matching belong in Phase 3.
- Compensation is not yet normalized across providers. Ashby compensation is available in its public response but is not persisted in this iteration.
- Source records and public job postings are shared across CareerPilot users; candidate profiles and resumes remain tenant-scoped.
