from pathlib import Path
from io import BytesIO
from pypdf import PdfReader
from docx import Document
import re

ALLOWED = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

def extract_text(content: bytes, mime_type: str) -> str:
    if mime_type == "application/pdf":
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
    raise ValueError("Only PDF and DOCX resumes are supported.")

def propose_facts(text: str) -> list[dict]:
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines() if x.strip()]
    facts = []
    if lines:
        first = lines[0][:200]
        if len(first.split()) <= 6 and not any(ch.isdigit() for ch in first):
            facts.append({"fact_key": "possible_name", "fact_value": first, "confidence": 0.35})
    skill_terms = [
        "python", "java", "javascript", "typescript", "react", "next.js", "node.js",
        "fastapi", "flask", "postgresql", "mysql", "mongodb", "docker", "kubernetes",
        "aws", "azure", "git", "jenkins", "machine learning", "sql", "c++", "excel"
    ]
    lowered = text.lower()
    for skill in skill_terms:
        if re.search(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])", lowered):
            facts.append({"fact_key": "skill", "fact_value": skill, "confidence": 0.75})
    emails = re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, flags=re.I)
    for email in sorted(set(emails)):
        facts.append({"fact_key": "email", "fact_value": email, "confidence": 0.95})
    return facts
