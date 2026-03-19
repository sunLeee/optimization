"""Type error fixture for mypy --strict testing.

This file intentionally contains type errors to verify mypy enforcement.
Do NOT fix these errors - they are required for CI validation.
"""


def add_numbers(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


# Intentional type error: passing str where int is expected
result: int = add_numbers("hello", "world")  # type: ignore[arg-type] -- remove to trigger error


def get_name() -> str:
    """Return a name."""
    return 42  # Intentional: returning int where str expected
