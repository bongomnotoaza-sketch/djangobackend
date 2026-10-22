"""
Stage 2 for get_definition:
    - Load nested definitions.json
    - Flatten to a {term: definition} dict
    - Look up by matched term
"""

import json
import os

_JSON_PATH = os.path.join(os.path.dirname(__file__), "definitions.json")


def _flatten(nested: dict) -> dict:
    """Flatten {Subject: {Topic: {term: def}}} -> {term: def}."""
    flat = {}
    for subject, topics in nested.items():
        for topic, entries in topics.items():
            for term, definition in entries.items():
                # Normalise apostrophes to match the extractor's normalise()
                key = term.lower().replace("’", "'")
                flat[key] = {
                    "term": term,
                    "definition": definition,
                    "subject": subject,
                    "topic": topic,
                }
    return flat


with open(_JSON_PATH, "r", encoding="utf-8") as f:
    _RAW = json.load(f)

DEFINITIONS = _flatten(_RAW)


def get_definition(matched_term: str):
    """
    Look up a definition by the exact term string produced by match_topic().

    Returns dict:
        {
          "term":       <str>,
          "definition": <str>,
          "subject":    <str>,   # 'Physics' | 'Chemistry'
          "topic":      <str>,   # e.g. 'Electrochemical Reactions'
        }
    or None if not found.
    """
    if not matched_term:
        return None
    key = matched_term.lower().replace("’", "'")
    return DEFINITIONS.get(key)


# ------------------------------------------------------------
# Self-test
# ------------------------------------------------------------
if __name__ == "__main__":
    for t in ["reduction", "momentum", "Ohm's law", "hydrolysis", "catalyst"]:
        print(t, "->", get_definition(t))