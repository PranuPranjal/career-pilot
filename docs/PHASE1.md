# Phase 1 implementation checklist

## Foundation
- [x] Monorepo directories
- [x] FastAPI and Next.js applications
- [x] Docker Compose for PostgreSQL and Redis
- [x] Environment template
- [x] Initial CI workflow
- [x] Alembic migration foundation

## Identity and tenant foundation
- [x] Tenant creation on registration
- [x] Password hashing
- [x] Login and short-lived JWT access token
- [x] Authenticated user dependency
- [x] Tenant-scoped profile, resume and fact queries
- [ ] Email verification and password reset
- [ ] Refresh-token rotation and session revocation
- [ ] MFA and production security review

## Candidate onboarding
- [x] Candidate profile model and endpoints
- [x] PDF/DOCX upload
- [x] Text extraction
- [x] Proposed facts and provenance
- [x] Confirm/reject extracted facts
- [x] Conversational onboarding starter
- [ ] OCR for scanned resumes
- [ ] LLM-backed extraction with structured schema and evaluation
- [ ] Full profile editor and conversation history UI

## Before real users
- [ ] Malware scanning and file signature validation
- [ ] Private object storage with encryption and signed URLs
- [ ] Rate limiting and abuse protection
- [ ] Tenant isolation integration tests
- [ ] Data export, deletion and retention controls
- [ ] Email delivery and account recovery
- [ ] Privacy/consent screens and legal review
