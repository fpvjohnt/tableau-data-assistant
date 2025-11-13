"""A lightweight stand-in for pandas used for testing.

This module implements a very small subset of the pandas API that is
required by the unit tests in this kata.  It is **not** a drop-in
replacement for the real pandas package, but it mimics the behaviour of
the specific methods and accessors that the data quality scorer relies
on.  The goal is to provide deterministic behaviour without depending on
external wheels that are unavailable in the execution environment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

import numpy as np


def _is_nan(value: Any) -> bool:
    """Return True if *value* should be considered missing."""

    if value is None:
        return True
    if isinstance(value, float):
        return np.isnan(value)
    if isinstance(value, np.generic):
        try:
            return np.isnan(value)
        except TypeError:  # pragma: no cover - defensive fallback
            return False
    return False


def _infer_dtype(values: Sequence[Any]) -> str:
    """Infer a simplified dtype string for a sequence of values."""

    non_missing = [v for v in values if not _is_nan(v)]
    if not non_missing:
        # Default to float to allow numeric aggregations when all values
        # are missing.
        return "float64"

    sample = non_missing[0]
    if all(isinstance(v, (bool, np.bool_)) for v in non_missing):
        return "bool"
    if all(isinstance(v, (int, np.integer)) for v in non_missing):
        return "int64"
    if all(isinstance(v, (int, float, np.integer, np.floating)) for v in non_missing):
        return "float64"
    if all(isinstance(v, datetime) for v in non_missing):
        return "datetime64"
    return "object"


class ColumnIndex(list):
    """Simple column index supporting boolean masks from Series."""

    def __getitem__(self, key):  # type: ignore[override]
        if isinstance(key, Series):
            return ColumnIndex([col for col, flag in zip(self, key) if flag])
        if isinstance(key, list) and key and all(isinstance(v, bool) for v in key):
            return ColumnIndex([col for col, flag in zip(self, key) if flag])
        return super().__getitem__(key)

    def tolist(self) -> List[str]:  # pragma: no cover - simple helper
        return list(self)


class Series:
    """A very small subset of pandas.Series."""

    def __init__(self, data: Iterable[Any], *, dtype: Optional[str] = None, index: Optional[List[Any]] = None, name: Optional[str] = None):
        self._data = list(data)
        self._index = list(index) if index is not None else list(range(len(self._data)))
        self.name = name
        self.dtype = dtype or _infer_dtype(self._data)

    # ------------------------------------------------------------------
    # Basic container protocol
    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __array__(self, dtype=None):  # pragma: no cover - behaviour covered indirectly
        return list(self._data)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Series(self._data[key], dtype=self.dtype, index=self._index[key], name=self.name)
        if isinstance(key, list) and key and all(isinstance(v, bool) for v in key):
            data = [value for value, flag in zip(self._data, key) if flag]
            index = [idx for idx, flag in zip(self._index, key) if flag]
            return Series(data, dtype=self.dtype, index=index, name=self.name)
        if isinstance(key, (int, np.integer)):
            return self._data[int(key)]
        if key in self._index:
            pos = self._index.index(key)
            return self._data[pos]
        raise KeyError(key)

    # ------------------------------------------------------------------
    # Representations
    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Series({self._data!r}, dtype={self.dtype!r})"

    # ------------------------------------------------------------------
    # Accessors
    @property
    def values(self) -> List[Any]:
        return list(self._data)

    def to_list(self) -> List[Any]:
        return list(self._data)

    def tolist(self) -> List[Any]:  # pragma: no cover - alias for pandas compatibility
        return self.to_list()

    # ------------------------------------------------------------------
    # Unary operations
    def isnull(self) -> "Series":
        return Series([_is_nan(value) for value in self._data], dtype="bool", index=self._index)

    def dropna(self) -> "Series":
        data = [v for v in self._data if not _is_nan(v)]
        index = [i for i, v in zip(self._index, self._data) if not _is_nan(v)]
        return Series(data, dtype=_infer_dtype(data), index=index, name=self.name)

    def astype(self, dtype: Any) -> "Series":
        if dtype is str or dtype == "str":
            data = ["nan" if _is_nan(v) else str(v) for v in self._data]
            return Series(data, dtype="object", index=self._index, name=self.name)
        raise TypeError(f"Unsupported dtype conversion: {dtype!r}")

    def any(self) -> bool:
        return any(bool(v) for v in self._data)

    def sum(self) -> Any:
        if self.dtype in {"bool", "int64", "float64"}:
            values = [v for v in self._data if not _is_nan(v)]
            return sum(values)
        raise TypeError("sum() only supported for numeric and boolean series")

    def max(self) -> Any:
        values = [v for v in self._data if not _is_nan(v)]
        return max(values) if values else None

    def quantile(self, q: float) -> float:
        values = [v for v in self._data if not _is_nan(v)]
        if not values:
            return float("nan")
        return float(np.quantile(values, q))

    # ------------------------------------------------------------------
    # Binary operations
    def _binary_op(self, other: Any, op) -> "Series":
        if isinstance(other, Series):
            if len(self) != len(other):
                raise ValueError("Series length mismatch")
            data = [op(a, b) for a, b in zip(self._data, other._data)]
        else:
            data = [op(a, other) for a in self._data]
        return Series(data, dtype="bool", index=self._index)

    def __eq__(self, other: Any) -> "Series":  # type: ignore[override]
        return self._binary_op(other, lambda a, b: a == b)

    def __ne__(self, other: Any) -> "Series":  # type: ignore[override]
        return self._binary_op(other, lambda a, b: a != b)

    def ne(self, other: Any) -> "Series":
        return self.__ne__(other)

    def __lt__(self, other: Any) -> "Series":
        return self._binary_op(other, lambda a, b: a < b)

    def __le__(self, other: Any) -> "Series":  # pragma: no cover - unused in tests
        return self._binary_op(other, lambda a, b: a <= b)

    def __gt__(self, other: Any) -> "Series":
        return self._binary_op(other, lambda a, b: a > b)

    def __ge__(self, other: Any) -> "Series":  # pragma: no cover - unused in tests
        return self._binary_op(other, lambda a, b: a >= b)

    def __or__(self, other: Any) -> "Series":
        return self._binary_op(other, lambda a, b: bool(a) or bool(b))

    def __and__(self, other: Any) -> "Series":  # pragma: no cover - unused in tests
        return self._binary_op(other, lambda a, b: bool(a) and bool(b))

    # ------------------------------------------------------------------
    # String accessor
    @property
    def str(self) -> "StringAccessor":
        if self.dtype != "object":
            raise AttributeError("String accessor is only available for object dtype")
        return StringAccessor(self)

    # ------------------------------------------------------------------
    # Datetime accessor
    @property
    def dt(self) -> "DateTimeAccessor":
        if self.dtype != "datetime64":
            raise AttributeError("Can only use .dt accessor with datetimelike values")
        return DateTimeAccessor(self)


class StringAccessor:
    def __init__(self, series: Series):
        self._series = series

    def strip(self) -> Series:
        data = [value.strip() for value in self._series._data]
        return Series(data, dtype="object", index=self._series._index, name=self._series.name)


class DateTimeAccessor:
    def __init__(self, series: Series):
        self._series = series

    @property
    def year(self) -> Series:
        data = [value.year if not _is_nan(value) else np.nan for value in self._series._data]
        return Series(data, dtype="int64", index=self._series._index, name=self._series.name)


class DataFrame:
    """A very small subset of pandas.DataFrame."""

    def __init__(self, data: Optional[Dict[str, Iterable[Any]]] = None):
        if not data:
            self._data: Dict[str, Series] = {}
            self.columns = ColumnIndex([])
            self._length = 0
            return

        processed: Dict[str, Series] = {}
        lengths = set()
        for name, values in data.items():
            sequence = list(values)
            lengths.add(len(sequence))
            processed[name] = Series(sequence, name=name)

        if len(lengths) > 1:
            raise ValueError("All columns must be the same length")

        self._data = processed
        self.columns = ColumnIndex(list(processed.keys()))
        self._length = lengths.pop() if lengths else 0

    # ------------------------------------------------------------------
    @property
    def shape(self) -> tuple[int, int]:
        return (self._length, len(self._data))

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, key: str) -> Series:
        return self._data[key]

    # ------------------------------------------------------------------
    def isnull(self) -> "DataFrame":
        return DataFrame({name: series.isnull() for name, series in self._data.items()})

    def _row_keys(self) -> List[tuple]:
        keys: List[tuple] = []
        for row_idx in range(self._length):
            row = []
            for name in self.columns:
                value = self._data[name]._data[row_idx]
                row.append("__NaN__" if _is_nan(value) else value)
            keys.append(tuple(row))
        return keys

    def duplicated(self, keep: str | bool = "first") -> Series:
        if keep not in ("first", "last", False):  # pragma: no cover - defensive
            raise ValueError("keep must be 'first', 'last', or False")

        row_keys = self._row_keys()
        counts = {}
        for key in row_keys:
            counts[key] = counts.get(key, 0) + 1

        if keep == "first":
            seen = set()
            flags = []
            for key in row_keys:
                if key in seen:
                    flags.append(True)
                else:
                    seen.add(key)
                    flags.append(False)
        elif keep == "last":  # pragma: no cover - unused in tests
            seen = set()
            flags = [False] * len(row_keys)
            for idx in range(len(row_keys) - 1, -1, -1):
                key = row_keys[idx]
                if key in seen:
                    flags[idx] = True
                else:
                    seen.add(key)
        else:  # keep False -> mark all duplicates
            flags = [counts[key] > 1 for key in row_keys]

        return Series(flags, dtype="bool")

    def select_dtypes(self, include: Optional[List[Any]] = None) -> "DataFrame":
        include = include or []

        def matches(dtype: str, candidate: Any) -> bool:
            if candidate in (np.number, float, int):
                return dtype in {"float64", "int64"}
            if isinstance(candidate, str) and candidate.startswith("datetime64"):
                return dtype.startswith("datetime64")
            return dtype == candidate

        selected: Dict[str, Series] = {}
        for name, series in self._data.items():
            if any(matches(series.dtype, candidate) for candidate in include):
                selected[name] = series
        return DataFrame(selected)

    def sum(self) -> Series:
        data = [series.sum() for series in self._data.values()]
        return Series(data, dtype="float64", index=list(self._data.keys()))

    def any(self) -> Series:
        data = [series.any() for series in self._data.values()]
        return Series(data, dtype="bool", index=list(self._data.keys()))


# ----------------------------------------------------------------------
# Module level helpers


def to_datetime(values: Iterable[Any]) -> List[datetime]:
    result = []
    for value in values:
        if isinstance(value, datetime):
            result.append(value)
        elif isinstance(value, str):
            result.append(datetime.fromisoformat(value))
        else:
            raise TypeError(f"Unsupported type for to_datetime: {type(value)!r}")
    return result


def date_range(start: str, periods: int) -> List[datetime]:
    start_dt = datetime.fromisoformat(start)
    return [start_dt + timedelta(days=i) for i in range(periods)]


@dataclass(frozen=True)
class Timestamp:
    value: datetime

    @staticmethod
    def now() -> datetime:
        return datetime.now()


# ----------------------------------------------------------------------
# Minimal pandas.api.types namespace


class _APITypes:
    @staticmethod
    def is_numeric_dtype(dtype: Any) -> bool:
        if isinstance(dtype, str):
            return dtype in {"int64", "float64"}
        return dtype in (int, float) or np.issubdtype(dtype, np.number)

    @staticmethod
    def is_string_dtype(dtype: Any) -> bool:
        if isinstance(dtype, str):
            return dtype == "object"
        return dtype is str

    @staticmethod
    def is_datetime64_any_dtype(dtype: Any) -> bool:
        if isinstance(dtype, str):
            return dtype.startswith("datetime64")
        return False


class _API:
    types = _APITypes()


api = _API()


__all__ = [
    "DataFrame",
    "Series",
    "Timestamp",
    "api",
    "date_range",
    "to_datetime",
]
