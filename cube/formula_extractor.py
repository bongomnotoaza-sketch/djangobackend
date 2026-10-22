"""
Stage 1 for get_formula:
    - Extract the formula topic from a free-text prompt
    - Match it against the keys in formulas.json (fuzzy-tolerant)
"""

import json
import os
import re
from difflib import SequenceMatcher

_JSON_PATH = os.path.join(os.path.dirname(__file__), "formulas.json")

with open(_JSON_PATH, "r", encoding="utf-8") as f:
    _RAW = json.load(f)


def _flatten_keys(nested):
    keys = []
    for subject, topics in nested.items():
        for topic, entries in topics.items():
            keys.extend(entries.keys())
    return keys


formula_keys = _flatten_keys(_RAW)


# ============================================================
# 1. Normalisation
# ============================================================
def normalise(text: str) -> str:
    """Lowercase, strip punctuation (keep apostrophes + Δ + Greek letters)."""
    text = text.lower()
    text = re.sub(r"[^\w\s'Δ°θλ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


_NORM_KEYS = [normalise(k) for k in formula_keys]


# ============================================================
# 2. Filler stripping
# ============================================================
FILLER_PHRASES = [
    # --- "formula/equation to calculate X" ---
    "what is the formula to calculate",
    "whats the formula to calculate",
    "what is formula to calculate",
    "whats formula to calculate",
    "what is the equation to calculate",
    "whats the equation to calculate",
    "what is equation to calculate",
    "whats equation to calculate",
    "formula to calculate",
    "equation to calculate",
    "formula for calculating",
    "equation for calculating",
    "formula used to calculate",
    "equation used to calculate",
    "formula to find",
    "equation to find",
    "formula for finding",
    "equation for finding",
    "formula to work out",
    "equation to work out",

    # --- "what is the formula for X" ---
    "what is the formula for",
    "whats the formula for",
    "what is formula for",
    "whats formula for",
    "what is the equation for",
    "whats the equation for",
    "what is equation for",
    "whats equation for",
    "give me the formula for",
    "give me the equation for",
    "give me formula for",
    "give me equation for",
    "tell me the formula for",
    "tell me the equation for",
    "tell me formula for",
    "tell me equation for",
    "show me the formula for",
    "show me the equation for",
    "show me formula for",
    "show me equation for",

    # --- "which/what formula do I use for" ---
    "what formula do i use for",
    "what equation do i use for",
    "what formula do i use to calculate",
    "what equation do i use to calculate",
    "which formula for",
    "which equation for",
    "which formula do i use",
    "which equation do i use",

    # --- "how do you calculate X" ---
    "how do you calculate",
    "how do i calculate",
    "how to calculate",
    "how can i calculate",
    "how do you find",
    "how do i find",
    "how to find",
    "how do you work out",
    "how do i work out",
    "how to work out",

    # --- "formula of / equation of X" ---
    "give me the formula of",
    "give me the equation of",
    "give me formula of",
    "give me equation of",
    "formula for",
    "equation for",
    "the formula for",
    "the equation for",
    "formula of",
    "equation of",
    "formula",
    "equation",

    # --- generic fillers ---
    "what is the",
    "what is",
    "whats the",
    "whats",
    "what's",
    "please",
    "can you",
    "could you",
    "i want to know",
    "let me know",
    "quick one",
    "hey",
    "yo",
    "again",
]


def strip_filler(prompt: str) -> str:
    """Remove intent words, leaving the topic phrase."""
    p = normalise(prompt)
    for phrase in sorted(FILLER_PHRASES, key=len, reverse=True):
        p = p.replace(phrase, " ")
    p = re.sub(r"\s+", " ", p).strip()
    return p


# ============================================================
# 3. Aliases — alternate phrasings → canonical keys
# ============================================================
ALIASES = {
    # --- Projectile motion variants ---
    "first equation of motion": "equations of motion",
    "second equation of motion": "equations of motion",
    "third equation of motion": "equations of motion",
    "fourth equation of motion": "equations of motion",
    "equation of motion": "equations of motion",
    "equations of motion": "equations of motion",
    "vertical projectile motion": "equations of motion",
    "projectile motion": "equations of motion",
    "projectile": "equations of motion",
    "free fall": "equations of motion",

    # --- Collision aliases ---
    "elastic collision formula": "elastic collision",
    "elastic collisions": "elastic collision",
    "inelastic collision formula": "inelastic collision",
    "inelastic collisions": "inelastic collision",
    "perfectly inelastic collision formula": "perfectly inelastic collision",
    "completely inelastic collision": "perfectly inelastic collision",
}


_NORM_ALIASES = {normalise(k): v for k, v in ALIASES.items()}


# ============================================================
# 4. Matching
# ============================================================
def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def match_formula(prompt: str, threshold: float = 0.45):
    """
    Extract the formula topic from a prompt and match against formula_keys.

    Returns:
        {
          "extracted": <str>,
          "matched":   <str|None>,
          "score":     <float>,
          "method":    'alias' | 'alias-substring' | 'exact'
                       | 'substring' | 'fuzzy' | 'none'
        }
    """
    extracted = strip_filler(prompt)

    if not extracted:
        return {"extracted": extracted, "matched": None,
                "score": 0.0, "method": "none"}

    # --- Pass 0: exact alias ---
    if extracted in _NORM_ALIASES:
        return {"extracted": extracted,
                "matched": _NORM_ALIASES[extracted],
                "score": 1.0, "method": "alias"}

    # --- Pass 0b: alias substring ---
    best_alias, best_alias_score = None, 0.0
    for norm_alias, canonical in _NORM_ALIASES.items():
        if norm_alias in extracted or extracted in norm_alias:
            score = min(len(extracted), len(norm_alias)) / max(len(extracted), len(norm_alias))
            if score > best_alias_score:
                best_alias, best_alias_score = canonical, score
    if best_alias is not None:
        return {"extracted": extracted, "matched": best_alias,
                "score": best_alias_score, "method": "alias-substring"}

    # --- Pass 1: exact ---
    for original, norm in zip(formula_keys, _NORM_KEYS):
        if extracted == norm:
            return {"extracted": extracted, "matched": original,
                    "score": 1.0, "method": "exact"}

    # --- Pass 2: substring (either way) ---
    best_sub, best_sub_score = None, 0.0
    for original, norm in zip(formula_keys, _NORM_KEYS):
        if extracted in norm or norm in extracted:
            score = min(len(extracted), len(norm)) / max(len(extracted), len(norm))
            if score > best_sub_score:
                best_sub, best_sub_score = original, score
    if best_sub is not None:
        return {"extracted": extracted, "matched": best_sub,
                "score": best_sub_score, "method": "substring"}

    # --- Pass 3: fuzzy ---
    best, best_score = None, 0.0
    for original, norm in zip(formula_keys, _NORM_KEYS):
        score = _similarity(extracted, norm)
        if score > best_score:
            best, best_score = original, score

    if best_score >= threshold:
        return {"extracted": extracted, "matched": best,
                "score": best_score, "method": "fuzzy"}

    return {"extracted": extracted, "matched": None,
            "score": best_score, "method": "none"}


# ============================================================
# Self-test
# ============================================================
if __name__ == "__main__":
    tests = [
        "what is the formula for momentum",
        "equation for kinetic energy",
        "how do you calculate net force",
        "formula for ohms law",
        "formula for ph",
        "equation for rms current",
        "give me the formula for net force",
        "which formula for kinetic energy",
        "formula for coulombs law",
        "how do you calculate electrical power",
        # alias-driven:
        "vertical projectile motion formula",
        "first equation of motion",
        "free fall equation",
        "elastic collision formula",
        "inelastic collision formula",
        "perfectly inelastic collision",
    ]
    for t in tests:
        r = match_formula(t)
        print(f"\nPrompt   : {t!r}")
        print(f"Extracted: {r['extracted']!r}")
        print(f"Matched  : {r['matched']!r}")
        print(f"Score    : {r['score']:.2f}  ({r['method']})")