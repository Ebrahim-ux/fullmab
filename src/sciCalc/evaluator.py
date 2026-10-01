"""Safe evaluator for scientific calculator expressions.

Expressions are parsed with Python's ``ast`` module and walked manually so
only an allow-listed set of operators and functions can ever execute -
arbitrary code (imports, attribute access, function defs, etc.) is rejected.
"""

from __future__ import annotations

import ast
import math
import operator
from collections.abc import Callable

Number = int | float


class CalculatorError(ValueError):
    """Raised when an expression is invalid or unsafe to evaluate."""


_BINARY_OPERATORS: dict[type[ast.operator], Callable[[Number, Number], Number]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[Number], Number]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _factorial(x: Number) -> Number:
    if x < 0 or x != int(x):
        raise CalculatorError("factorial is only defined for non-negative integers")
    return math.factorial(int(x))


def _abs(x: Number) -> Number:
    return abs(x)


_FUNCTIONS: dict[str, Callable[..., Number]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "exp": math.exp,
    "abs": _abs,
    "factorial": _factorial,
    "radians": math.radians,
    "degrees": math.degrees,
}

_CONSTANTS: dict[str, Number] = {
    "pi": math.pi,
    "e": math.e,
}


def evaluate(expression: str) -> Number:
    """Evaluate a scientific-calculator expression and return a number.

    Raises CalculatorError on invalid syntax, unsupported names, or
    mathematically undefined operations (e.g. division by zero).
    """
    expression = expression.strip()
    if not expression:
        raise CalculatorError("expression is empty")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError(f"invalid syntax: {exc.msg}") from exc

    try:
        return _eval_node(tree.body)
    except ZeroDivisionError as exc:
        raise CalculatorError("division by zero") from exc
    except (OverflowError, ValueError) as exc:
        raise CalculatorError(str(exc)) from exc


def _eval_node(node: ast.AST) -> Number:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise CalculatorError(f"unsupported literal: {node.value!r}")

    if isinstance(node, ast.BinOp):
        op_func = _BINARY_OPERATORS.get(type(node.op))
        if op_func is None:
            raise CalculatorError(f"unsupported operator: {type(node.op).__name__}")
        return op_func(_eval_node(node.left), _eval_node(node.right))

    if isinstance(node, ast.UnaryOp):
        unary_op_func = _UNARY_OPERATORS.get(type(node.op))
        if unary_op_func is None:
            raise CalculatorError(f"unsupported operator: {type(node.op).__name__}")
        return unary_op_func(_eval_node(node.operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise CalculatorError("unsupported function call")
        func = _FUNCTIONS.get(node.func.id)
        if func is None:
            raise CalculatorError(f"unknown function: {node.func.id}")
        if node.keywords:
            raise CalculatorError("keyword arguments are not supported")
        args = [_eval_node(arg) for arg in node.args]
        return func(*args)

    if isinstance(node, ast.Name):
        if node.id in _CONSTANTS:
            return _CONSTANTS[node.id]
        raise CalculatorError(f"unknown identifier: {node.id}")

    raise CalculatorError(f"unsupported expression: {type(node).__name__}")
