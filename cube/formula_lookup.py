"""
Stage 2 for get_formula:
    - Load nested formulas.json
    - Flatten to {key: {formula, subject, topic}}
    - Look up by matched key
"""

import json
import os

_JSON_PATH = os.path.join(os.path.dirname(__file__), "formulas.json")


def _flatten(nested: dict) -> dict:
    flat = {}
    for subject, topics in nested.items():
        for topic, entries in topics.items():
            for key, formula in entries.items():
                flat[key.lower().replace("’", "'")] = {
                    "key": key,
                    "formula": formula,
                    "subject": subject,
                    "topic": topic,
                }
    return flat


with open(_JSON_PATH, "r", encoding="utf-8") as f:
    _RAW = json.load(f)

FORMULAS = _flatten(_RAW)


def get_formula(matched_key: str):
    """
    Look up a formula by its key (as returned by match_formula).

    Returns:
        {
          "key":     <str>,
          "formula": <str>,
          "subject": <str>,   # 'Physics' | 'Chemistry' | 'Financial Mathematics'
                              # | 'Sequences and Series' | 'Functions and Graphs'
                              # | 'Statistics' | 'Analytical Geometry'
                              # | 'Trigonometry' | 'Euclidean Geometry'
          "topic":   <str>,
        }
    or None if not found.
    """
    if not matched_key:
        return None
    return FORMULAS.get(matched_key.lower().replace("’", "'"))


if __name__ == "__main__":
    for k in [
        # Physics
        "momentum",
        "kinetic energy",
        "ohms law",
        "rms current",
        "net force",
        "electrical power",
        "standard cell potential",
        # Chemistry
        "ph",
        "number of moles",
        "molar concentration",
        # Financial Mathematics
        "simple interest",
        "simple interest amount",
        "compound interest",
        "present value",
        "effective rate",
        "compound growth time",
        "straight line depreciation",
        "reducing balance depreciation",
        "inflation",
        "future value of annuity",
        "present value of annuity",
        "sinking fund payment",
        "loan repayment",
        "outstanding balance",
        # Sequences and Series
        "arithmetic nth term",
        "arithmetic difference",
        "arithmetic sum",
        "arithmetic mean",
        "geometric ratio",
        "geometric nth term",
        "geometric sum",
        "infinite geometric sum",
        "convergence condition",
        "geometric mean",
        "geometric n",
        # Functions and Graphs
        "linear",
        "gradient",
        "point gradient",
        "quadratic",
        "axis of symmetry",
        "quadratic formula",
        "discriminant",
        "hyperbola",
        "hyperbola vertical asymptote",
        "hyperbola horizontal asymptote",
        "exponential",
        "transformed exponential",
        "logarithmic",
        "exponential log relationship",
        "product log law",
        "quotient log law",
        "power log law",
        "change of base",
        "composition",
        "inverse",
        # Statistics
        "mean",
        "frequency mean",
        "class midpoint",
        "range",
        "q1 position",
        "median q2 position",
        "q3 position",
        "iqr",
        "variance",
        "alternative variance",
        "standard deviation",
        "lower outlier fence",
        "upper outlier fence",
        "1 sd",
        "2 sd",
        "3 sd",
        # Analytical Geometry
        "distance",
        "midpoint",
        "analytical gradient",
        "straight line",
        "analytical point gradient",
        "parallel",
        "perpendicular",
        "inclination",
        "angle between lines",
        "circle",
        "circle at origin",
        "radius",
        "tangent gradient",
        "radius perpendicular tangent",
        # Trigonometry
        "trig sine",
        "trig cosine",
        "trig tangent",
        "tan identity",
        "pythagorean identity",
        "sine compound",
        "cos compound",
        "tan compound",
        "double sine",
        "double cosine",
        "double tangent",
        "sine rule",
        "cosine rule",
        "triangle area",
        "sine period",
        "graph period",
        "amplitude",
        # Euclidean Geometry
        "geometry straight line",
        "around a point",
        "vertically opposite",
        "triangle angles",
        "exterior angle",
        "corresponding angles",
        "alternate angles",
        "co interior angles",
        "isosceles triangle",
        "congruency",
        "similarity",
        "similar sides",
        "similar areas",
        "pythagoras",
        "angle at centre",
        "same segment",
        "semicircle",
        "cyclic quadrilateral",
        "geometry radius perpendicular tangent",
        "tangents from same point",
        "tangent chord",
        "centre perpendicular chord",
        "equal chords",
    ]:
        print(k, "->", get_formula(k))