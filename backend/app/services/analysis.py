from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.services.documents import analyze_document_text as _legacy_analyze
from app.services.timeline import extract_events


def analyze_academic_document(text: str, filename: str) -> dict[str, Any]:
    """Produce twin-oriented structured data; the legacy service may use OpenAI when configured."""
    base = _legacy_analyze(text, filename)
    lines = [line.strip().lstrip("#").strip() for line in text.splitlines() if line.strip()]
    modules = _module_hierarchy(lines, base.get("modules", []), base.get("topics", []))
    events = extract_events(lines)
    return {
        **base,
        "subject_code": _first_match(lines, r"\b(?:course|subject)\s*(?:code|no\.?|number)?\s*[:#-]\s*([A-Z]{2,}[\s-]?\d{2,}[A-Z]?)"),
        "instructor": _first_match(lines, r"\b(?:instructor|lecturer|faculty|professor)\s*[:\-]\s*(.+)"),
        "semester": _first_match(lines, r"\b((?:spring|summer|fall|autumn|winter)\s*(?:semester)?|semester\s*\d+)\b"),
        "academic_year": _first_match(lines, r"\b(20\d{2}\s*[-/]\s*20\d{2})\b"),
        "learning_outcomes": _marked(lines, r"(?:learning\s+outcomes?|course\s+outcomes?|upon\s+completion)\s*[:\-]?\s*(.+)"),
        "references": _marked(lines, r"(?:references?|textbooks?|reading)\s*[:\-]?\s*(.+)"),
        "topic_hierarchy": modules,
        "timeline_events": events,
    }


def _module_hierarchy(lines: list[str], fallback_modules: list[str], fallback_topics: list[str]) -> list[dict]:
    groups: list[dict] = []
    current = None
    for line in lines:
        match = re.match(r"(?:module|unit|chapter|week)\s*\d*\s*[:\-]?\s*(.+)", line, re.I)
        if match:
            current = {"name": match.group(0).strip(), "topics": []}; groups.append(current); continue
        if current and re.match(r"(?:[-*•]|\d+[.)])\s*.+", line):
            value = re.sub(r"^(?:[-*•]|\d+[.)])\s*", "", line).strip()
            if 2 < len(value) < 120:
                current["topics"].append(value)
    if not groups:
        groups = [{"name": name, "topics": []} for name in fallback_modules]
    if groups and fallback_topics:
        groups[0]["topics"] = list(dict.fromkeys(groups[0]["topics"] + fallback_topics))
    return [{"name": group["name"], "topics": list(dict.fromkeys(group["topics"]))[:20]} for group in groups]


def _marked(lines: list[str], pattern: str) -> list[str]:
    return list(dict.fromkeys(match.group(1).strip() for line in lines if (match := re.search(pattern, line, re.I))))[:20]


def _first_match(lines: list[str], pattern: str) -> str | None:
    for line in lines:
        match = re.search(pattern, line, re.I)
        if match:
            return match.group(1).strip(" .")
    return None
