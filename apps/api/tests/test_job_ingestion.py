import unittest
from unittest.mock import patch
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db import Base
from app.models import JobSource, JobPosting
from app.services.job_ingestion import sync_source

class FakeResponse:
    def __init__(self, jobs):
        self.jobs = jobs
    def raise_for_status(self):
        return None
    def json(self):
        return {"jobs": self.jobs}

class JobIngestionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.source = JobSource(provider="greenhouse", company_name="Example Co", board_token="example")
        self.session.add(self.source)
        self.session.commit()
        self.session.refresh(self.source)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    @patch("app.services.job_sources.greenhouse.httpx.get")
    def test_sync_upserts_same_job(self, get):
        get.return_value = FakeResponse([{
            "id": 1001, "title": "Backend Engineer", "location": {"name": "India"},
            "content": "<p>Python</p>", "absolute_url": "https://example.com/jobs/1001"
        }])
        first = sync_source(self.session, self.source)
        second = sync_source(self.session, self.source)
        self.assertEqual(first["created"], 1)
        self.assertEqual(second["created"], 0)
        self.assertEqual(second["updated"], 1)
        self.assertEqual(len(self.session.scalars(select(JobPosting)).all()), 1)

    @patch("app.services.job_sources.greenhouse.httpx.get")
    def test_empty_feed_does_not_mark_all_jobs_stale(self, get):
        get.return_value = FakeResponse([{
            "id": 1001, "title": "Backend Engineer", "location": {"name": "India"},
            "content": "Python", "absolute_url": "https://example.com/jobs/1001"
        }])
        sync_source(self.session, self.source)
        get.return_value = FakeResponse([])
        result = sync_source(self.session, self.source)
        job = self.session.scalar(select(JobPosting))
        self.assertEqual(result["marked_stale"], 0)
        self.assertEqual(job.status, "active")

if __name__ == "__main__":
    unittest.main()
