import re
from dataclasses import dataclass
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


@dataclass
class RegexCheck:
    DEFAULT_MESSAGE = "string didn't match {regex}"

    regex: str | re.Pattern[str]
    message_template: str

    def match(self, value: str) -> bool:
        compiled = re.compile(self.regex)
        return bool(compiled.match(value))

    @property
    def message(self) -> str:
        return self.message_template.format(regex=self.regex)


class RegexTest(ISchemaTest):
    def __init__(self, checks: list[RegexCheck]) -> None:
        super().__init__()
        self._checks = checks

    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        if not isinstance(val, str):
            return ValidationResult.err(ValidationError("invalid type", path, "regex"))

        for check in self._checks:
            if not check.match(val):
                return ValidationResult.err(
                    ValidationError(check.message, path, "regex")
                )
        return ValidationResult.ok(val)


class CoerceStringTest(ISchemaTest):
    def __init__(self, coerce: bool) -> None:
        super().__init__()
        self._coerce = coerce

    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        value: Any = val

        if not self._coerce:
            if not isinstance(value, str):
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) is not of type int", path, "coerce"
                    )
                )
        elif not isinstance(value, str):
            if isinstance(value, int):
                value = str(value)
            elif isinstance(value, float):
                value = str(value)
            else:
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) cannot be cast to type str",
                        path,
                        "coerce",
                    )
                )
        return ValidationResult.ok(cast(T, value))


class _String[R](ISchemaType["_String[R]", R]):
    def __init__(self) -> None:
        super().__init__()
        self._range = Range[int]()
        self._enum = set[R]()
        self._regex: list[RegexCheck] = []

    def min(self, val: int, *, inclusive: bool = True) -> "_String[R]":
        self._range.min = RangePoint(val, RangePointType.is_inclusive(inclusive))
        return self

    def max(self, val: int, *, inclusive: bool = True) -> "_String[R]":
        self._range.max = RangePoint(val, RangePointType.is_inclusive(inclusive))
        return self

    def nullable(self) -> "_String[str | None]":
        return cast(OptionalString, super().nullable())

    def enum(self, *values: R) -> "_String[R]":
        self._enum = set(values)
        return self

    def regex(
        self, pattern: str | re.Pattern[str], error_description: str | None = None
    ) -> "_String[R]":
        self._regex.append(
            RegexCheck(
                regex=pattern,
                message_template=error_description or RegexCheck.DEFAULT_MESSAGE,
            )
        )
        return self

    def email(self) -> "_String[R]":
        return self.regex(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
            "string is not a valid email",
        )

    def url(self) -> "_String[R]":
        return self.regex(
            r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            "string is not a valid url",
        )

    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[R]:
        path = path or []

        result = self._test_nullable(value, path)

        if not result or result.value is None:
            return cast(ValidationResult[R], result)

        result.update(
            CoerceStringTest(self._coerce).test(result.unwrap_or(value), path)
        )

        if not result:
            return cast(ValidationResult[R], result)

        for test in [
            EnumSchemaTest(self._enum),
            RegexTest(self._regex),
        ]:
            result.update(test.test(result.unwrap_or(value), path))

        if not result:
            return cast(ValidationResult[R], result)

        if not (
            range_result := RangeSchemaTest(self._range).test(
                len(result.unwrap_or(value) or ""), path
            )
        ):
            result.invalidate(range_result.error)

        return cast(ValidationResult[R], result)


String = _String[str]
OptionalString = _String[str | None]
