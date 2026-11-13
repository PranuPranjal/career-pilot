import httpx
from .base import JobSourceAdapter, NormalizedJob, parse_datetime, html_to_text

class GreenhouseAdapter(JobSourceAdapter):
    provider = "greenhouse"
    def fetch(self, board_token: str) -> list[NormalizedJob]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        response = httpx.get(url, params={"content": "true"}, timeout=25, follow_redirects=True)
        response.raise_for_status()
        payload = response.json()
        jobs = []
        for item in payload.get("jobs", []):
            content = item.get("content") or ""
            departments = item.get("departments") or []
            jobs.append(NormalizedJob(
                external_id=str(item.get("id")), title=item.get("title") or "Untitled role",
                company_name=item.get("company_name") or "", location=(item.get("location") or {}).get("name", ""),
                department=", ".join(x.get("name", "") for x in departments if x.get("name")),
                description_html=content, description_text=html_to_text(content),
                job_url=item.get("absolute_url") or "", apply_url=item.get("absolute_url") or "",
                published_at=parse_datetime(item.get("first_published")), source_updated_at=parse_datetime(item.get("updated_at"))
            ))
        return [j for j in jobs if j.external_id and j.job_url]
