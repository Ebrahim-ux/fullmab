import math

import pytest

from sciCalc.evaluator import CalculatorError, evaluate


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2 + 3", 5),
        ("2 - 3", -1),
        ("4 * 5", 20),
        ("10 / 4", 2.5),
        ("2 ** 10", 1024),
        ("-5 + 2", -3),
        ("(2 + 3) * 4", 20),
        ("sqrt(16)", 4),
        ("factorial(5)", 120),
        ("log(100)", 2),
        ("abs(-7)", 7),
        ("pi", math.pi),
        ("e", math.e),
    ],
)
def test_evaluate_valid_expressions(expression: str, expected: float) -> None:
    assert evaluate(expression) == pytest.approx(expected)


def test_evaluate_trig_uses_radians() -> None:
    assert evaluate("sin(0)") == pytest.approx(0)
    assert evaluate("cos(0)") == pytest.approx(1)


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "   ",
        "1 +",
        "1 / 0",
        "__import__('os')",
        "os.system('ls')",
        "unknown_var",
        "unknown_func(1)",
        "factorial(-1)",
        "factorial(1.5)",
        "1; 2",
    ],
)
def test_evaluate_rejects_invalid_expressions(expression: str) -> None:
    with pytest.raises(CalculatorError):
        evaluate(expression)
