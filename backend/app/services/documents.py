from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any


try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    fitz = None

try:
    from docx import Document as DocxDocument  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    DocxDocument = None

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Image = None

try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "will",
    "week",
    "module",
    "unit",
    "chapter",
    "lecture",
    "course",
    "syllabus",
    "topic",
}


def extract_text_from_document(file_path: Path) -> tuple[str, int, str]:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    if suffix == ".docx":
        return _extract_docx(file_path)
    return _extract_txt(file_path)


def analyze_document_text(text: str, filename: str, course_hint: str | None = None) -> dict[str, Any]:
    openai_payload = _analyze_with_openai(text, filename, course_hint)
    if openai_payload is not None:
        return openai_payload
    return _heuristic_analysis(text, filename, course_hint)


def _extract_pdf(file_path: Path) -> tuple[str, int, str]:
    if fitz is None:
        raise RuntimeError("PDF extraction requires PyMuPDF")

    document = fitz.open(file_path)
    page_count = document.page_count
    text = "\n".join(page.get_text("text") for page in document).strip()
    if text:
        return text, page_count, "pymupdf"

    if pytesseract is None or Image is None:
        raise RuntimeError("PDF OCR fallback requires pytesseract and pillow")

    extracted_pages: list[str] = []
    for page in document:
        pixmap = page.get_pixmap(dpi=220)
        image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        extracted_pages.append(pytesseract.image_to_string(image))
    return "\n".join(extracted_pages).strip(), page_count, "ocr"


def _extract_docx(file_path: Path) -> tuple[str, int, str]:
    if DocxDocument is None:
        raise RuntimeError("DOCX extraction requires python-docx")

    document = DocxDocument(file_path)
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    text = "\n".join(paragraphs).strip()
    page_count = max(1, len(paragraphs) // 18 or 1)
    return text, page_count, "docx"


def _extract_txt(file_path: Path) -> tuple[str, int, str]:
    text = file_path.read_text(encoding="utf-8", errors="ignore").strip()
    return text, max(1, text.count("\f") + 1), "text"


def _analyze_with_openai(text: str, filename: str, course_hint: str | None) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None

    client = OpenAI(api_key=api_key)
    prompt = (
        "Extract academic structure from this syllabus. Return only valid JSON with keys: "
        "course_name, topics, modules, important_concepts, assignments_mentioned, exam_dates, "
        "recommended_study_priority. Do not summarize. Convert the document into structured data."
    )
    message = f"Filename: {filename}\nCourse hint: {course_hint or 'unknown'}\n\nDocument text:\n{text[:24000]}"
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    payload = json.loads(content)
    return _normalize_analysis(payload, filename, course_hint)


def _heuristic_analysis(text: str, filename: str, course_hint: str | None) -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    course_name = _infer_course_name(filename, lines, course_hint)
    topics = _extract_marked_items(lines, [r"^topic[:\-]\s*(.+)$", r"^topics[:\-]\s*(.+)$", r"^learning outcomes?[:\-]\s*(.+)$"])
    modules = _extract_marked_items(lines, [r"^module[:\-]\s*(.+)$", r"^unit[:\-]\s*(.+)$", r"^week\s*\d+[:\-]\s*(.+)$"])
    assignments = _extract_marked_items(lines, [r"assignment", r"project", r"homework", r"lab", r"quiz", r"assessment"])
    exam_dates = _extract_exam_dates(lines)
    important_concepts = _extract_concepts(lines, topics + modules + assignments)
    priority = _recommend_priority(assignments, exam_dates, topics, modules)
    return _normalize_analysis(
        {
            "course_name": course_name,
            "topics": topics,
            "modules": modules,
            "important_concepts": important_concepts,
            "assignments_mentioned": assignments,
            "exam_dates": exam_dates,
            "recommended_study_priority": priority,
        },
        filename,
        course_hint,
    )


def _normalize_analysis(payload: dict[str, Any], filename: str, course_hint: str | None) -> dict[str, Any]:
    course_name = str(payload.get("course_name") or course_hint or _course_from_filename(filename))
    return {
        "course_name": course_name,
        "topics": _unique_strings(payload.get("topics")),
        "modules": _unique_strings(payload.get("modules")),
        "important_concepts": _unique_strings(payload.get("important_concepts")),
        "assignments_mentioned": _unique_strings(payload.get("assignments_mentioned")),
        "exam_dates": _unique_strings(payload.get("exam_dates")),
        "recommended_study_priority": str(payload.get("recommended_study_priority") or "Medium"),
    }


def _course_from_filename(filename: str) -> str:
    stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"\b(syllabus|outline|notes|lecture|plan|document)\b", "", stem, flags=re.I)
    course = re.sub(r"\s+", " ", stem).strip(" -_")
    return course.title() if course else "Untitled Course"


def _infer_course_name(filename: str, lines: list[str], course_hint: str | None) -> str:
    if course_hint:
        return course_hint.strip()
    for line in lines[:15]:
        if 3 <= len(line.split()) <= 8 and not re.search(r"\b(week|module|unit|assignment|exam|quiz|lab)\b", line, re.I):
            return line.title()
    return _course_from_filename(filename)


def _extract_marked_items(lines: list[str], patterns: list[str]) -> list[str]:
    items: list[str] = []
    for line in lines:
        lowered = line.lower()
        matched = any(re.search(pattern, lowered, re.I) for pattern in patterns)
        if matched:
            cleaned = re.sub(r"^[\-*•\d.\s]+", "", line).strip()
            cleaned = re.sub(r"^(topic|topics|module|modules|unit|units|week\s*\d+|assignment|project|homework|lab|quiz|assessment)[:\-]\s*", "", cleaned, flags=re.I)
            if cleaned:
                items.append(cleaned)
    return _unique_strings(items[:24])


def _extract_exam_dates(lines: list[str]) -> list[str]:
    items: list[str] = []
    date_pattern = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|[A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?)\b")
    for line in lines:
        if re.search(r"\b(exam|test|midterm|final|assessment)\b", line, re.I):
            matches = date_pattern.findall(line)
            items.extend(matches or [line.strip()])
    return _unique_strings(items)


def _extract_concepts(lines: list[str], seed_items: list[str]) -> list[str]:
    words: Counter[str] = Counter()
    for line in lines:
        if len(line) > 120:
            continue
        tokens = re.findall(r"[A-Za-z][A-Za-z\-]+", line.lower())
        for token in tokens:
            if len(token) > 2 and token not in STOPWORDS:
                words[token] += 1
    concepts = [word.replace("-", " ").title() for word, _ in words.most_common(12)]
    concepts.extend(item for item in seed_items[:6] if item)
    return _unique_strings(concepts)[:12]


def _recommend_priority(assignments: list[str], exam_dates: list[str], topics: list[str], modules: list[str]) -> str:
    pressure = len(assignments) * 1.2 + len(exam_dates) * 2 + len(topics) * 0.35 + len(modules) * 0.25
    if pressure >= 10:
        return "High"
    if pressure >= 5:
        return "Medium"
    return "Low"


def _unique_strings(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    seen: set[str] = set()
    items: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        items.append(text)
    return items