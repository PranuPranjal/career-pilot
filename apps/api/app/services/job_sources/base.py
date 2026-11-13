from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class NormalizedJob:
    external_id: str
    title: str
    company_name: str
    location: str = ""
    department: str = ""
    employment_type: str = ""
    workplace_type: str = ""
    description_text: str = ""
    description_html: str = ""
    job_url: str = ""
    apply_url: str = ""
    published_at: datetime | None = None
    source_updated_at: datetime | None = None

class JobSourceAdapter:
    provider: str
    def fetch(self, board_token: str) -> list[NormalizedJob]:
        raise NotImplementedError


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed
    except (TypeError, ValueError):
        return None


def html_to_text(value: str) -> str:
    from html import unescape
    import re
    value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value or "")
    value = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()
