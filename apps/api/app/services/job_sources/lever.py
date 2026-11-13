import httpx
from .base import JobSourceAdapter, NormalizedJob, parse_datetime, html_to_text

class LeverAdapter(JobSourceAdapter):
    provider = "lever"
    def fetch(self, board_token: str) -> list[NormalizedJob]:
        url = f"https://api.lever.co/v0/postings/{board_token}"
        response = httpx.get(url, params={"mode": "json"}, timeout=25, follow_redirects=True)
        response.raise_for_status()
        payload = response.json()
        jobs = []
        for item in payload if isinstance(payload, list) else []:
            categories = item.get("categories") or {}
            description = item.get("description") or item.get("descriptionPlain") or ""
            location = categories.get("location") or ", ".join(categories.get("allLocations") or [])
            jobs.append(NormalizedJob(
                external_id=str(item.get("id")), title=item.get("text") or "Untitled role",
                company_name=item.get("company") or "", location=location,
                department=categories.get("department") or categories.get("team") or "",
                employment_type=categories.get("commitment") or "",
                workplace_type="Remote" if item.get("workplaceType") == "remote" else "",
                description_html=item.get("description") or "", description_text=html_to_text(description),
                job_url=item.get("hostedUrl") or item.get("applyUrl") or "", apply_url=item.get("applyUrl") or item.get("hostedUrl") or "",
                published_at=parse_datetime(item.get("createdAt")), source_updated_at=parse_datetime(item.get("updatedAt"))
            ))
        return [j for j in jobs if j.external_id and j.job_url]
