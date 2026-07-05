"""Boolean schema definition."""

from typing import Any, cast

from pyaddict.schema.base import (
    ISchemaTest,
    ISchemaType,
)
from pyaddict.schema.result import ValidationError, ValidationResult


class _CoerceBoolTest(ISchemaTest):
    def __init__(self, coerce: bool) -> None:
        super().__init__()
        self._coerce = coerce

    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        value: Any = val

        if not self._coerce:
            if not isinstance(value, bool):
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) is not of type bool", path, "coerce"
                    )
                )
        elif not isinstance(value, bool):
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes", "y"):
                    value = True
                elif value.lower() in ("false", "0", "no", "n"):
                    value = False
            elif isinstance(value, int):
                value = bool(value)
            if not isinstance(value, bool):
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) cannot be cast to type int",
                        path,
                        "coerce",
                    )
                )
        return ValidationResult.ok(cast(T, value))


class _Boolean[R](ISchemaType["_Boolean[R]", R]):
    def __init__(self) -> None:
        super().__init__()

    def nullable(self) -> "_Boolean[bool | None]":
        return cast(OptionalBoolean, super().nullable())

    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[R]:
        path = path or []

        result = self._test_nullable(value, path)

        if not result or result.value is None:
            return cast(ValidationResult[R], result)

        for test in [_CoerceBoolTest(self._coerce)]:
            result.update(test.test(result.unwrap_or(value), path))

        return cast(ValidationResult[R], result)


Boolean = _Boolean[bool]
OptionalBoolean = _Boolean[bool | None]
