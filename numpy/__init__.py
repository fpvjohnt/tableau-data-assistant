"""A tiny subset of NumPy used for unit testing.

The real NumPy package cannot be installed in the execution environment,
so this module implements just enough functionality for the tests in this
repository.  Only the functions and attributes that are actually used by
the project are provided here.
"""

from __future__ import annotations


import builtins
import math
import random as _random
from typing import Iterable, Iterator, List, Sequence


nan = float("nan")
inf = float("inf")
bool_ = bool
integer = int
floating = float


class generic:  # pragma: no cover - compatibility shim
    """Placeholder for numpy.generic."""


class number(float):  # pragma: no cover - compatibility shim
    """Placeholder type for numpy.number."""


class _Array:
    """Lightweight sequence supporting a few NumPy-like operations."""

    def __init__(self, data: Iterable[float]):
        self._data = list(data)

    def __iter__(self) -> Iterator[float]:
        return iter(self._data)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._data)

    def __add__(self, other):
        if isinstance(other, _Array):
            return _Array(a + b for a, b in zip(self._data, other._data))
        return _Array(a + other for a in self._data)

    def __radd__(self, other):  # pragma: no cover - same as __add__
        return self.__add__(other)

    def __sub__(self, other):  # pragma: no cover - unused but kept for completeness
        if isinstance(other, _Array):
            return _Array(a - b for a, b in zip(self._data, other._data))
        return _Array(a - other for a in self._data)

    def __mul__(self, other):
        if isinstance(other, _Array):  # pragma: no cover - defensive
            return _Array(a * b for a, b in zip(self._data, other._data))
        return _Array(a * other for a in self._data)

    def __rmul__(self, other):  # pragma: no cover - same as __mul__
        return self.__mul__(other)

    def __truediv__(self, other):  # pragma: no cover - unused but present for safety
        if isinstance(other, _Array):
            return _Array(a / b for a, b in zip(self._data, other._data))
        return _Array(a / other for a in self._data)

    def sum(self) -> float:
        return float(math.fsum(self._data))

    def tolist(self) -> List[float]:  # pragma: no cover - convenience
        return list(self._data)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"_Array({self._data!r})"


def _ensure_iterable(values: Sequence[float]) -> List[float]:
    if isinstance(values, _Array):
        return values._data
    if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
        return list(values)
    if hasattr(values, "__iter__") and not isinstance(values, (str, bytes, dict)):
        return list(values)
    return [values]  # type: ignore[list-item]


def quantile(values: Sequence[float], q: float) -> float:
    data = sorted(v for v in _ensure_iterable(values) if not math.isnan(v))
    if not data:
        return float("nan")
    idx = q * (len(data) - 1)
    lower = int(math.floor(idx))
    upper = int(math.ceil(idx))
    if lower == upper:
        return float(data[lower])
    frac = idx - lower
    return float(data[lower] + (data[upper] - data[lower]) * frac)


def abs(values):
    if isinstance(values, _Array):
        return _Array(abs(v) for v in values)
    return builtins.abs(values)  # type: ignore[name-defined]


def sqrt(value):
    if isinstance(value, _Array):  # pragma: no cover - not used in tests
        return _Array(math.sqrt(v) for v in value)
    return math.sqrt(value)


def isnan(value):
    if isinstance(value, _Array):  # pragma: no cover - unused in tests
        return _Array(math.isnan(v) for v in value)
    try:
        return math.isnan(value)
    except TypeError:
        return False


def isinf(value):
    if isinstance(value, _Array):
        return _Array(math.isinf(v) for v in value)
    if isinstance(value, (list, tuple)):
        return _Array(math.isinf(v) if isinstance(v, (int, float)) else False for v in value)
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes, dict)):
        return _Array(math.isinf(v) if isinstance(v, (int, float)) else False for v in value)
    return math.isinf(value) if isinstance(value, (int, float)) else False


def issubdtype(dtype, target) -> bool:
    if isinstance(dtype, str) and target in (number, float, int):
        return dtype in {"int64", "float64"}
    return False


class _Random:
    @staticmethod
    def randn(size: int) -> _Array:
        return _Array(_random.gauss(0, 1) for _ in range(size))


random = _Random()


__all__ = [
    "_Array",
    "abs",
    "bool_",
    "floating",
    "generic",
    "inf",
    "integer",
    "isinf",
    "isnan",
    "issubdtype",
    "nan",
    "number",
    "quantile",
    "random",
    "sqrt",
]
