# exceptions.py
"""
App-level exception so the rest of the Django app never has to import
instructor's internals directly. This is the exact protection you needed
earlier — instructor's exception import path moved between versions
(instructor.exceptions vs instructor.v2.core.errors), which crashed your
except block. Wrapping it here means that if it moves again, you only
fix services.py — every view/caller importing from here is unaffected.
"""


class IntentClassificationFailed(Exception):
    """Raised when the model can't produce a valid intent after retries."""