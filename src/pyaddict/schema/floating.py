"""Float schema definition."""

from typing import Any, cast

from pyaddict.schema.base import (
    ISchemaTest,
    ISchemaType,
    Range,
    RangePoint,
    RangePointType,
)
from pyaddict.schema.common import EnumSchemaTest, RangeSchemaTest
from pyaddict.schema.result import ValidationError, ValidationResult


class _CoerceFloatTest(ISchemaTest):
    def __init__(self, coerce: bool) -> None:
        super().__init__()
        self._coerce = coerce

    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        value: Any = val

        if not self._coerce:
            if not isinstance(value, float):
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) is not of type float", path, "coerce"
                    )
                )
        elif not isinstance(value, float):
            if isinstance(value, str):
                value = float(value)
            elif isinstance(value, int):
                value = float(value)
            else:
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) cannot be cast to type float",
                        path,
                        "coerce",
                    )
                )
        return ValidationResult.ok(cast(T, value))


class _Float[R](ISchemaType["_Float[R]", R]):
    def __init__(self) -> None:
        super().__init__()
        self._range = Range[float]()
        self._enum: set[R] = set()

    def min(self, val: float, *, inclusive: bool = True) -> "_Float[R]":
        self._range.min = RangePoint(val, RangePointType.is_inclusive(inclusive))
        return self

    def max(self, val: float, *, inclusive: bool = True) -> "_Float[R]":
        self._range.max = RangePoint(val, RangePointType.is_inclusive(inclusive))
        return self

    def enum(self, *values: R) -> "_Float[R]":
        self._enum = set(values)
        return self

    def nullable(self) -> "_Float[float | None]":
        return cast(OptionalFloat, super().nullable())

    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[R]:
        path = path or []

        result = self._test_nullable(value, path)

        if not result or result.value is None:
            return cast(ValidationResult[R], result)

        result.update(
            _CoerceFloatTest(self._coerce).test(result.unwrap_or(value), path)
        )

        if not result:
            return cast(ValidationResult[R], result)

        for test in [RangeSchemaTest(self._range), EnumSchemaTest(self._enum)]:
            result.update(test.test(result.unwrap_or(value), path))

        return cast(ValidationResult[R], result)


Float = _Float[float]
OptionalFloat = _Float[float | None]
