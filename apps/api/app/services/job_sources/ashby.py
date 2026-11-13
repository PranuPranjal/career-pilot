import httpx
from .base import JobSourceAdapter, NormalizedJob, parse_datetime, html_to_text

class AshbyAdapter(JobSourceAdapter):
    provider = "ashby"
    def fetch(self, board_token: str) -> list[NormalizedJob]:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{board_token}"
        response = httpx.get(url, params={"includeCompensation": "true"}, timeout=25, follow_redirects=True)
        response.raise_for_status()
        payload = response.json()
        jobs = []
        for item in payload.get("jobs", []):
            if item.get("isListed") is False:
                continue
            location = item.get("location") or ""
            secondary = [x.get("location") for x in item.get("secondaryLocations", []) if x.get("location")]
            if secondary:
                location = ", ".join([location, *secondary]).strip(", ")
            description_html = item.get("descriptionHtml") or ""
            description_text = item.get("descriptionPlain") or html_to_text(description_html)
            jobs.append(NormalizedJob(
                external_id=item.get("jobUrl") or item.get("applyUrl") or f"{item.get('title')}:{location}",
                title=item.get("title") or "Untitled role", company_name="", location=location,
                department=item.get("department") or item.get("team") or "",
                employment_type=item.get("employmentType") or "", workplace_type=item.get("workplaceType") or "",
                description_text=description_text, description_html=description_html,
                job_url=item.get("jobUrl") or "", apply_url=item.get("applyUrl") or item.get("jobUrl") or "",
                published_at=parse_datetime(item.get("publishedAt")), source_updated_at=parse_datetime(item.get("publishedAt"))
            ))
        return [j for j in jobs if j.external_id and j.job_url]
