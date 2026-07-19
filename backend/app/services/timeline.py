from __future__ import annotations

from datetime import datetime
import re

DATE = re.compile(r"\b(?:\d{4}-\d{1,2}-\d{1,2}|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?\s+\d{1,2}(?:,?\s+\d{4})?)\b", re.I)
KINDS = (("final", "final"), ("midterm", "midterm"), ("quiz", "quiz"), ("assignment", "assignment"), ("project", "project"), ("cat", "assessment"), ("exam", "exam"))


def extract_events(lines: list[str]) -> list[dict]:
    events, seen = [], set()
    for line in lines:
        match = DATE.search(line)
        if not match:
            continue
        kind = next((name for token, name in KINDS if token in line.lower()), None)
        if not kind:
            continue
        title = re.sub(r"\s+", " ", line).strip(" -:|")
        key = (title.casefold(), match.group(0).casefold())
        if key in seen:
            continue
        seen.add(key)
        events.append({"event": title, "date": match.group(0), "priority": "High" if kind in {"final", "midterm", "exam"} else "Medium", "kind": kind})
    return events


def parse_event_date(value: str):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y", "%B %d", "%b %d"):
        try:
            parsed = datetime.strptime(value.replace(".", ""), fmt)
            return parsed.replace(year=datetime.now().year) if parsed.year == 1900 else parsed
        except ValueError:
            pass
    return None
