import json
from typing import Any, cast

from pyaddict.schema.base import (
    ISchemaTest,
    ISchemaType,
    Range,
    RangePoint,
    RangePointType,
    Validatable,
)
from pyaddict.schema.common import RangeSchemaTest, validate
from pyaddict.schema.result import ValidationError, ValidationResult


class CoerceArrayTest(ISchemaTest):
    def __init__(self, coerce: bool) -> None:
        super().__init__()
        self._coerce = coerce

    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        value: Any = val

        if not self._coerce:
            if not isinstance(value, list):
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) is not of type list", path, "coerce"
                    )
                )
        elif not isinstance(value, list):
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            if not isinstance(value, list):
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) cannot be cast to type list",
                        path,
                        "coerce",
                    )
                )
        return ValidationResult.ok(cast(T, value))


class _Array[R](ISchemaType["_Array[R]", R]):
    def __init__(self, item: Validatable | None = None) -> None:
        super().__init__()
        self._range = Range[int]()
        self._item = item
        self._item_at: dict[int, Validatable] = {}

    def min(self, val: int, *, inclusive: bool = True) -> "_Array[R]":
        self._range.min = RangePoint(val, RangePointType.is_inclusive(inclusive))
        return self

    def max(self, val: int, *, inclusive: bool = True) -> "_Array[R]":
        self._range.max = RangePoint(val, RangePointType.is_inclusive(inclusive))
        return self

    def includes(self, schema: Validatable, *, at_index: int) -> "_Array[R]":
        self._item_at[at_index] = schema
        return self

    def nullable(self) -> "_Array[list[Any] | None]":
        return cast(OptionalArray, super().nullable())

    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[R]:
        path = path or []

        result = self._test_nullable(value, path)

        if not result or result.value is None:
            return cast(ValidationResult[R], result)

        for test in [CoerceArrayTest(self._coerce)]:
            result.update(test.test(result.unwrap_or(value), path))

        list_like = result.unwrap_or(value)

        if isinstance(list_like, list) and not (
            range_result := RangeSchemaTest(self._range).test(
                len(result.unwrap_or(value) or ""), path
            )
        ):
            result.invalidate(range_result.error)

        if isinstance(value, list):
            failed: list[ValidationError] = []

            if self._item is not None:
                for i, item in enumerate(value):
                    item_result = validate(
                        item,
                        self._item,
                        path=[*path, f"[{i}]"],
                    )
                    if not item_result and item_result.error:
                        failed.append(item_result.error)

            for i, schema in self._item_at.items():
                try:
                    item = value[i]
                    item_result = validate(item, schema, path=[*path, f"[{i}]"])
                    if not item_result and item_result.error:
                        failed.append(item_result.error)
                except IndexError:
                    failed.append(
                        ValidationError(
                            f"index {i} out of bounds (length: {len(value)})",
                            path,
                            "schema_at",
                        )
                    )

            if failed:
                result.invalidate(
                    error=ValidationError(
                        "items do not match schema", path, "schema", cause=failed
                    )
                )

        return cast(ValidationResult[R], result)


Array = _Array[list[Any]]
OptionalArray = _Array[list[Any] | None]
