"""Anything schema definition."""

from typing import Any, cast

from pyaddict.schema.base import ISchemaType
from pyaddict.schema.result import ValidationResult


class _Anything[R](ISchemaType["_Anything[R]", R]):
    def nullable(self) -> "_Anything[R | None]":
        return cast(OptionalAnything, super().nullable())

    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[Any | None]:
        path = path or []

        result = self._test_nullable(value, path)

        if not result or result.value is None:
            return result

        return ValidationResult.ok(value)


Anything = _Anything[Any]
OptionalAnything = _Anything[Any | None]
