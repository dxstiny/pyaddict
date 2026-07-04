from typing import Any

from pyaddict.schema.base import (
    ISchemaTest,
    ISchemaType,
    Range,
    RangePointType,
    Validatable,
)
from pyaddict.schema.result import ValidationError, ValidationResult


class EnumSchemaTest[R](ISchemaTest):
    def __init__(self, items: set[R]) -> None:
        super().__init__()
        self._items = items

    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        if not self._items or val in self._items:
            return ValidationResult.ok(val)
        return ValidationResult.err(
            ValidationError(f"{val} is not in {self._items}", path, "enum")
        )


class RangeSchemaTest(ISchemaTest):
    def __init__(self, range: Range | None = None) -> None:
        super().__init__()
        self._range = range

    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        if not self._range:
            return ValidationResult.ok(val)

        if self._range.min and val is not None:
            if (
                self._range.min.type == RangePointType.INCLUSIVE
                and val < self._range.min.point
            ):
                return ValidationResult.err(
                    ValidationError(
                        f"expected {val} to be greater than or equal to {
                            self._range.min.point
                        }",
                        [],
                        "min",
                    )
                )
            if (
                self._range.min.type == RangePointType.EXCLUSIVE
                and val <= self._range.min.point
            ):
                return ValidationResult.err(
                    ValidationError(
                        f"expected {val} to be greater than {self._range.min.point}",
                        [],
                        "min",
                    )
                )
        if self._range.max and val is not None:
            if (
                self._range.max.type == RangePointType.INCLUSIVE
                and val > self._range.max.point
            ):
                return ValidationResult.err(
                    ValidationError(
                        f"expected {val} to be less than or equal to {
                            self._range.max.point
                        }",
                        [],
                        "min",
                    )
                )
            if (
                self._range.max.type == RangePointType.EXCLUSIVE
                and val >= self._range.max.point
            ):
                return ValidationResult.err(
                    ValidationError(
                        f"expected {val} to be less than {self._range.max.point}",
                        [],
                        "min",
                    )
                )
        return ValidationResult.ok(val)


def validate(
    val: Any, schema: Validatable, *, path: list[str]
) -> ValidationResult[Any]:
    if isinstance(schema, ISchemaType):
        return schema.validate(val, path=path)
    if val == schema:
        return ValidationResult.ok(val)
    return ValidationResult.err(
        ValidationError(f"{val} does not equal {schema}", path, "equals")
    )
