"""
split_by_topics.py

Reads NSC Physical Sciences PDFs (paper1/paper2 + memo1/memo2) for each
year folder in papers/, splits them into sub-questions by searching for
the labels listed in the hand-curated maps in topics/, tags each with a
topic, and writes:

    topics_output/
        2025_paper1/
            newtons_laws.json
            ...
            _index.json
            _unmatched.json                 (only if any)
        2025_paper2/
            ...
        2024_paper1/
            ...
        ...

Maps expected at (4 files per year):
    topics/2025_paper1_question_map.json
    topics/2025_paper1_answer_map.json
    topics/2025_paper2_question_map.json
    topics/2025_paper2_answer_map.json

A (year, paper) is processed only if BOTH its map files exist.
Missing years/paper maps are skipped with a logged message.

IMPORTANT: topics_output/ is wiped at the start of every run.

Extraction strategy:
    Rather than trying to *discover* sub-question labels via regex (which
    breaks whenever a label appears mid-line, after a footer, or glued to
    a symbol), this script takes the label list from the map files as the
    source of truth and searches for each label literally, using digit/dot
    boundary lookarounds so '10.1' does not match inside '10.1.2'.
"""

import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

import pymupdf as fitz  # PyMuPDF (new name; fitz alias still works)


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path("papers")
TOPICS_DIR = Path("topics")
OUTPUT_DIR = Path("topics_output")

# Mojibake fixes for DBE symbol fonts
MOJIBAKE_FIXES = {
    "яБР": "✓", "яАа": "", "яАп": "",
    "тАв": "•", "тАУ": "–", "тАФ": "—",
    "тАШ": "'", "тАЭ": '"', "тАЬ": '"',
    "тИТ": "−", "тИЖ": "Δ", "тИЩ": "·", "тИЪ": "√",
    "тБД": "⁄", "тЙа": "≠", "тЙе": "≥", "тЙд": "≤",
    "╬╕": "θ", "╬Ф": "Δ", "╬й": "Ω", "╬╗": "λ",
    "╬н": "ν", "╬╝": "μ", "╬╡": "ε", "╬▒": "α",
    "╞Р": "ε", "╘Р": "ε", "╬е": "Σ",
    "┬╡": "μ", "┬║": "°", "┬╖": "·",
    "├Ч": "×", "├╖": "÷", "├п": "ï",
}


# ============================================================
# TEXT HELPERS
# ============================================================

def fix_mojibake(text: str) -> str:
    for bad, good in MOJIBAKE_FIXES.items():
        text = text.replace(bad, good)
    return text


def clean(text: str) -> str:
    text = fix_mojibake(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pages(pdf_path: Path):
    doc = fitz.open(pdf_path)
    try:
        return [
            {"page": i + 1, "text": page.get_text("text")}
            for i, page in enumerate(doc)
        ]
    finally:
        doc.close()


def build_full_text(pages):
    full = ""
    offsets = []
    for p in pages:
        offsets.append((len(full), p["page"]))
        full += p["text"] + "\n"
    return full, offsets


def page_for_offset(offsets, off):
    if not offsets:
        return None
    page = offsets[0][1]
    for char_off, pg in offsets:
        if char_off <= off:
            page = pg
        else:
            break
    return page


# ============================================================
# LABEL SEARCH (driven by the map files, not by regex discovery)
# ============================================================

def find_label_spans(full_text: str, labels):
    """
    For each label in `labels`, find its first occurrence in `full_text`
    that is not part of a longer label (e.g. '10.1' must not match inside
    '10.1.1' or '10.1.2').

    Returns a list of (label, start, end) sorted by start position.
    """
    # Longest first, so '10.1.2' is tried before '10.1'
    ordered = sorted(set(labels), key=len, reverse=True)

    hits = []
    for label in ordered:
        # Escape dots; require the match not to be flanked by digit/dot
        # so '10.1' won't match inside '10.1.2'.
        pattern = re.compile(
            r"(?<![\d.])" + re.escape(label) + r"(?![\d.])"
        )
        m = pattern.search(full_text)
        if m:
            hits.append((label, m.start(), m.end()))

    hits.sort(key=lambda t: t[1])

    # Drop any hit fully contained inside an earlier, longer hit
    # (shouldn't happen with the lookarounds above, but cheap insurance)
    filtered = []
    last_end = -1
    for label, s, e in hits:
        if s >= last_end:
            filtered.append((label, s, e))
            last_end = e
    return filtered


def slice_by_labels(full_text: str, labels, clean_fn):
    """
    Return {label: {"text": ..., "start": int, "end": int}} by slicing
    full_text between consecutive known labels.
    """
    spans = find_label_spans(full_text, labels)
    out = {}
    for i, (label, s, e) in enumerate(spans):
        end = spans[i + 1][1] if i + 1 < len(spans) else len(full_text)
        out[label] = {
            "text": clean_fn(full_text[s:end]),
            "start": s,
            "end": end,
        }
    return out


# ============================================================
# BUILD RECORDS
# ============================================================

def build_records(paper_pages, memo_pages, question_map, answer_map):
    """
    question_map: {label -> topic} from the paper side
    answer_map:   {label -> topic} from the memo side (for validation)
    Returns (records, unmatched).
    """
    paper_full, paper_offsets = build_full_text(paper_pages)
    memo_full, memo_offsets = (
        build_full_text(memo_pages) if memo_pages else ("", [])
    )

    q_labels = list(question_map.keys())
    a_labels = list(answer_map.keys())

    paper_slices = slice_by_labels(paper_full, q_labels, clean)
    memo_slices = (
        slice_by_labels(memo_full, a_labels, clean) if memo_full else {}
    )

    records = []
    unmatched = []

    for label in q_labels:
        q = paper_slices.get(label)
        if q is None:
            # Label in map but not found in paper PDF — flag it, still emit.
            records.append({
                "label": label,
                "topic": question_map[label],
                "question": None,
                "answer": None,
                "paper_pages": None,
                "memo_pages": None,
                "topic_mismatch": None,
                "missing_in": ["paper"],
            })
            unmatched.append(label)
            continue

        paper_page_range = [
            page_for_offset(paper_offsets, q["start"]),
            page_for_offset(paper_offsets, max(q["end"] - 1, q["start"])),
        ]

        m = memo_slices.get(label)
        if m is None:
            answer = None
            memo_page_range = None
            missing = ["memo"]
        else:
            answer = m["text"]
            memo_page_range = [
                page_for_offset(memo_offsets, m["start"]),
                page_for_offset(memo_offsets, max(m["end"] - 1, m["start"])),
            ]
            missing = []

        if answer is None:
            unmatched.append(label)

        memo_topic = answer_map.get(label)
        topic_mismatch = (
            memo_topic is not None
            and question_map[label] != "unmapped"
            and memo_topic != question_map[label]
        )

        records.append({
            "label": label,
            "topic": question_map[label],
            "question": q["text"],
            "answer": answer,
            "paper_pages": paper_page_range,
            "memo_pages": memo_page_range,
            "topic_mismatch": topic_mismatch or None,
            "missing_in": missing or None,
        })

    return records, unmatched


# ============================================================
# LOAD MAPS (per year AND paper)
# ============================================================

def load_maps(year: int, paper: str):
    """
    Load the two maps for a specific (year, paper).
    Returns (question_map, answer_map, missing_filenames).
    """
    q_file = TOPICS_DIR / f"{year}_{paper}_question_map.json"
    a_file = TOPICS_DIR / f"{year}_{paper}_answer_map.json"

    missing = []
    if not q_file.exists():
        missing.append(q_file.name)
    if not a_file.exists():
        missing.append(a_file.name)
    if missing:
        return None, None, missing

    with open(q_file, encoding="utf-8") as f:
        q_data = json.load(f)
    with open(a_file, encoding="utf-8") as f:
        a_data = json.load(f)

    def _strip(data):
        return {k: v for k, v in data.items()
                if re.match(r"^\d+\.\d+", k)}

    return _strip(q_data), _strip(a_data), []


# ============================================================
# WRITE OUTPUT
# ============================================================

def write_output(year: int, paper: str, records: list, unmatched: list):
    year_paper_dir = OUTPUT_DIR / f"{year}_{paper}"
    year_paper_dir.mkdir(parents=True, exist_ok=True)

    by_topic = defaultdict(list)
    for r in records:
        by_topic[r["topic"]].append(r)

    for topic, items in sorted(by_topic.items()):
        with open(year_paper_dir / f"{topic}.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "year": year,
                    "paper": paper,
                    "topic": topic,
                    "count": len(items),
                    "questions": items,
                },
                f, indent=2, ensure_ascii=False,
            )

    with open(year_paper_dir / "_index.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "year": year,
                "paper": paper,
                "total_sub_questions": len(records),
                "topics": {t: len(v) for t, v in sorted(by_topic.items())},
                "unmatched_count": len(unmatched),
            },
            f, indent=2, ensure_ascii=False,
        )

    if unmatched:
        with open(year_paper_dir / "_unmatched.json", "w", encoding="utf-8") as f:
            json.dump(
                {"year": year, "paper": paper,
                 "unmatched_labels": sorted(unmatched)},
                f, indent=2, ensure_ascii=False,
            )

    return len(records), len(by_topic), len(unmatched)


# ============================================================
# PROCESS ONE (YEAR, PAPER)
# ============================================================

def process(year: int, paper: str, question_map, answer_map):
    year_dir = BASE_DIR / str(year)
    paper_pdf = year_dir / f"{paper}.pdf"
    memo_pdf = year_dir / f"memo{paper[-1]}.pdf"

    if not paper_pdf.exists():
        print(f"      {paper_pdf.name} missing — skipping")
        return

    print(f"      Reading {paper_pdf.name}")
    paper_pages = extract_pages(paper_pdf)

    memo_pages = []
    if memo_pdf.exists():
        print(f"      Reading {memo_pdf.name}")
        memo_pages = extract_pages(memo_pdf)
    else:
        print(f"      {memo_pdf.name} missing — answers will be null")

    records, unmatched = build_records(
        paper_pages, memo_pages, question_map, answer_map
    )

    n, t, u = write_output(year, paper, records, unmatched)
    print(f"      Wrote {n} sub-questions across {t} topics "
          f"({u} unmatched answers)")


# ============================================================
# MAIN
# ============================================================

def main():
    # Wipe previous output so every run starts clean
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        print(f"Cleared existing output: {OUTPUT_DIR.resolve()}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    TOPICS_DIR.mkdir(parents=True, exist_ok=True)

    year_dirs = sorted(
        (d for d in BASE_DIR.iterdir() if d.is_dir() and d.name.isdigit()),
        key=lambda d: int(d.name),
    )
    if not year_dirs:
        print(f"No year folders in {BASE_DIR.resolve()}")
        return

    for year_dir in year_dirs:
        year = int(year_dir.name)
        print(f"\n{'=' * 60}\nYear: {year}\n{'=' * 60}")

        for paper in ("paper1", "paper2"):
            question_map, answer_map, missing = load_maps(year, paper)

            if question_map is None:
                print(f"   -> {paper}: skipping — missing map file(s): "
                      f"{', '.join(missing)}")
                continue

            print(f"   -> {paper}")
            print(f"      Loaded maps: {len(question_map)} question labels, "
                  f"{len(answer_map)} answer labels")
            process(year, paper, question_map, answer_map)

    print("\nDONE")


if __name__ == "__main__":
    main()