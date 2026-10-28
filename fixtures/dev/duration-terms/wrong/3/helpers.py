"""JSON domain checks, with no coercion or external effects.

Lists remain caller-owned. Task code must build its own output containers.
Booleans are intentionally excluded from the integer domain.
String values retain spelling, whitespace and Unicode code points.
"""


def sequence(value):
    """Require an actual JSON-style array."""
    if not isinstance(value, list):
        raise ValueError("expected list")
    return value


def mapping(value):
    """Require a JSON object with string keys."""
    if not isinstance(value, dict):
        raise ValueError("expected object")
    if any(not isinstance(key, str) for key in value):
        raise ValueError("expected string keys")
    return value


def integer(value):
    """Do not accept bool as an integer."""
    if type(value) is not int:
        raise ValueError("expected integer")
    return value


def text(value):
    """Do not trim, normalize or stringify input implicitly."""
    if not isinstance(value, str):
        raise ValueError("expected string")
    return value
