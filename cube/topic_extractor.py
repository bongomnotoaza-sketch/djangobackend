"""
Stage 1 for get_definition:
    - Extract the topic from a free-text prompt
    - Match it against the known `terms` list (fuzzy-tolerant)
"""

import re
from difflib import SequenceMatcher


# ============================================================
# Your known terms (from terms.txt)
# ============================================================
terms = [
    # Newton's Laws
    "normal force",
    "frictional force",
    "static frictional force",
    "kinetic frictional force",
    "Newton's first law of motion",
    "Newton's second law of motion",
    "Newton's third law of motion",
    "Newton's Law of Universal Gravitation",
    "weight",

    # Momentum and Impulse
    "momentum",
    "Newton's second law of motion in terms of momentum",
    "impulse",
    "system",
    "internal forces",
    "external forces",
    "isolated system",
    "principle of conservation of linear momentum",

    # Vertical Projectile Motion
    "projectile",
    "free fall",

    # Work, Energy and Power
    "work done on an object by a constant force F",
    "work-energy theorem",
    "conservative force",
    "non-conservative force",
    "principle of conservation of mechanical energy",
    "power",

    # Doppler Effect
    "Doppler effect",
    "red shifts",

    # Electrostatics
    "Coulomb's law",
    "electric field",
    "electric field at a point",

    # Electric Circuits
    "Ohm's law",
    "power",
    "emf",

    # Electrodynamics
    "rms potential difference",
    "rms current",

    # Optical Phenomena
    "photoelectric effect",
    "threshold frequency",
    "work function",
    "atomic absorption spectrum",
    "atomic emission spectrum",

    # Chemical Change
    "balanced chemical equations",

    # Quantitative Aspects
    "molar volume of gases",
    "volume relationships in gaseous reactions",

    # Intermolecular Forces
    "dipole-dipole forces",
    "induced dipole forces or London forces",
    "hydrogen bonding",
    "intermolecular forces",
    "interatomic forces (intramolecular forces)",
    "boiling point",
    "melting point",
    "vapour pressure",

    # Organic Molecules
    "organic molecules",
    "molecular formula",
    "structural formula",
    "condensed structural formula",
    "hydrocarbon",
    "homologous series",
    "saturated compounds",
    "unsaturated compounds",
    "functional group",
    "structural isomer",
    "chain isomers",
    "positional isomers",
    "functional isomers",
    "esterification",
    "hydrolysis",
    "cracking of alkanes",

    # Energy and Change
    "heat of reaction (ΔH)",
    "exothermic reactions",
    "endothermic reactions",
    "activation energy",
    "activated complex",

    # Rate and Extent of Reaction
    "reaction rate",
    "collision theory",
    "catalyst",

    # Chemical Equilibrium
    "open system",
    "closed system",
    "reversible reaction",
    "chemical equilibrium",
    "Le Chatelier's principle",

    # Acids and Bases
    "Arrhenius theory",
    "Lowry-Bronsted theory",
    "strong acids",
    "weak acids",
    "strong bases",
    "weak bases",
    "concentrated acids/bases",
    "dilute acids/bases",
    "ampholyte",
    "hydrolysis",
    "equivalence point",
    "endpoint",
    "pH scale",
    "Kw",
    "auto-ionisation of water",

    # Electrochemical Reactions
    "galvanic cell",
    "oxidation",
    "reduction",
    "oxidising agent",
    "reducing agent",
    "anode",
    "cathode",
    "electrolyte",
    "electrolytic cell",
    "electrolysis",
]


# ============================================================
# 1. Normalisation helpers
# ============================================================
def normalise(text: str) -> str:
    """Lowercase, strip punctuation (except apostrophes), collapse spaces."""
    text = text.lower()
    # keep apostrophes for Newton's, Coulomb's, Ohm's, Le Chatelier's
    text = re.sub(r"[^\w\s'Δ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Precompute normalised terms once
_NORM_TERMS = [normalise(t) for t in terms]


# ============================================================
# 2. Stopword / filler stripping
# ============================================================
# These are the "intent" words that carry no topic information.
FILLER_PHRASES = [
    "what is the meaning of",
    "what is the definition of",
    "definition of",
    "meaning of",
    "what does",
    "what is",
    "what are",
    "whats",
    "what's",
    "define",
    "explain",
    "describe",
    "tell me about",
    "tell me",
    "about",
    "mean",
    "means",
    "please",
    "can you",
    "could you",
    "i want to know",
    "let me know",
    "quick one",
    "hey",
    "yo",
    "in physics",
    "in physical science",
    "in chemistry",
    "in science",
]


def strip_filler(prompt: str) -> str:
    """Remove intent words, leaving only the topic phrase."""
    p = normalise(prompt)
    # longer phrases first, so 'what is the meaning of' beats 'what is'
    for phrase in sorted(FILLER_PHRASES, key=len, reverse=True):
        p = p.replace(phrase, " ")
    p = re.sub(r"\s+", " ", p).strip()
    return p


# ============================================================
# 3. Matching
# ============================================================
def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def match_topic(prompt: str, threshold: float = 0.55):
    """
    Extract topic from prompt and match against `terms`.

    Returns dict:
        {
          "extracted": <str>,        # cleaned topic phrase from prompt
          "matched":   <str|None>,   # best term in `terms`
          "score":     <float>,      # similarity score 0..1
          "method":    <str>,        # 'exact' | 'substring' | 'fuzzy' | 'none'
        }
    """
    extracted = strip_filler(prompt)

    if not extracted:
        return {"extracted": extracted, "matched": None,
                "score": 0.0, "method": "none"}

    # --- Pass 1: exact match ---
    for original, norm in zip(terms, _NORM_TERMS):
        if extracted == norm:
            return {"extracted": extracted, "matched": original,
                    "score": 1.0, "method": "exact"}

    # --- Pass 2: substring match (either way) ---
    # e.g. "newtons second law" inside "newton's second law of motion"
    best_sub, best_sub_score = None, 0.0
    for original, norm in zip(terms, _NORM_TERMS):
        if extracted in norm or norm in extracted:
            # prefer the term whose length ratio is closest to 1
            score = min(len(extracted), len(norm)) / max(len(extracted), len(norm))
            if score > best_sub_score:
                best_sub, best_sub_score = original, score
    if best_sub is not None:
        return {"extracted": extracted, "matched": best_sub,
                "score": best_sub_score, "method": "substring"}

    # --- Pass 3: fuzzy match ---
    best, best_score = None, 0.0
    for original, norm in zip(terms, _NORM_TERMS):
        score = _similarity(extracted, norm)
        if score > best_score:
            best, best_score = original, score

    if best_score >= threshold:
        return {"extracted": extracted, "matched": best,
                "score": best_score, "method": "fuzzy"}

    return {"extracted": extracted, "matched": None,
            "score": best_score, "method": "none"}


# ============================================================
# 4. Quick demo / self-test
# ============================================================
if __name__ == "__main__":
    test_prompts = [
        "what is velocity",                      # not in terms → no match
        "what is momentum",                      # exact
        "define momentum",                       # exact
        "what is the meaning of newton's second law of motion",
        "explain newton's second law",
        "what is newton's 2nd law",              # fuzzy / substring
        "tell me about the doppler effect",
        "what is coulombs law",
        "whats ohms law",
        "define pH scale",
        "what is le chatelier's principle",
        "what is free fall",
        "explain work energy theorem",
        "what is a galvanic cell",
        "what is the photoelectric effect",
        "define an anode",
        "what is an electrolyte",
        "what's a catalyst",
        "what is hydrolysis",
        "what is frictional force",
        "what is static friction",
        "explain the normal force",
        "what is emf",
        "what is rms current",
        "define a hydrocarbon",
        "what is an isomer",
        "what is esterification",
        "what is an exothermic reaction",
        "what is endothermic reaction",
        "tell me about activation energy",
        "what is hydrogen bonding",
        "define vapour pressure",
        "what is the boiling point",
        "what is an equivalence point",
        "define an oxidising agent",
        "what is reduction",
        "explain electrolysis",
        "what is the atomic emission spectrum",
        "what is work function",
        "what is threshold frequency",
    ]

    for p in test_prompts:
        r = match_topic(p)
        print(f"\nPrompt   : {p!r}")
        print(f"Extracted: {r['extracted']!r}")
        print(f"Matched  : {r['matched']!r}")
        print(f"Score    : {r['score']:.2f}  ({r['method']})")