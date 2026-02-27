"""
tools/calculator.py
Safe arithmetic calculator tool for budget computations.
"""

import logging
from crewai.tools import tool

logger = logging.getLogger(__name__)

# Only these characters are permitted in expressions
_ALLOWED_CHARS = set("0123456789+-*/(). ")


@tool("Calculator")
def calculator(expression: str) -> str:
    """
    Evaluate a safe arithmetic expression for budget calculations.
    Use this to add up costs, multiply nightly rates by days,
    compute percentages, or verify budget totals.
    Input : a Python arithmetic expression, e.g. '70 * 7 + 35 * 7 + 200'
    Output: the numeric result as a string.
    Do NOT pass variable names or function calls – numbers and operators only.
    """
    logger.debug("[Calculator] Expression: %s", expression)

    # Strip whitespace and validate characters
    cleaned = expression.strip()
    if not cleaned:
        return "Error: Empty expression."

    if not all(c in _ALLOWED_CHARS for c in cleaned):
        forbidden = [c for c in cleaned if c not in _ALLOWED_CHARS]
        return (
            f"Error: Expression contains forbidden characters: {forbidden}. "
            "Only numbers and + - * / ( ) are allowed."
        )

    try:
        # Restrict builtins for safety
        result = eval(cleaned, {"__builtins__": {}})  # noqa: S307
        logger.debug("[Calculator] Result: %s", result)
        return str(round(float(result), 2))
    except ZeroDivisionError:
        return "Error: Division by zero."
    except SyntaxError:
        return f"Error: Invalid expression syntax – '{cleaned}'."
    except Exception as e:
        return f"Error: {str(e)}"
