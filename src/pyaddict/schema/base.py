from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

from pyaddict.schema.result import ValidationError, ValidationResult


class ISchemaType[C, T](ABC):
    def __init__(self) -> None:
        self._default: T | None = None
        self._coerce: bool = False
        self._nullable: bool = False
        self._optional: bool = False

    def coerce(self) -> C:
        self._coerce = True
        return cast(C, self)

    def default(self, value: T) -> C:
        self._default = value
        return cast(C, self)

    def optional(self) -> C:
        self._optional = True
        return cast(C, self)

    @property
    def default_value(self) -> T | None:
        return self._default

    @property
    def is_optional(self) -> bool:
        return self._optional

    @abstractmethod
    def nullable(self) -> Any:
        self._nullable = True
        return self

    @abstractmethod
    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[Any]:
        """
        validates the value

        returns a ValidationResult,
        which contains an error if the value is invalid
        or the value if valid
        """

    def _test_nullable[R](self, value: R, path: list[str]) -> ValidationResult[R]:
        if value is None:
            if self._nullable:
                return ValidationResult.ok(cast(R, self._default), True)
            else:
                return ValidationResult.err(
                    ValidationError("unexpected null value", path, "nullable")
                )
        return ValidationResult.ok(value, nullable=self._nullable)


SchemaType = ISchemaType[Any, Any]
Primitive = int | float | bool | str | dict | list
Validatable = SchemaType | Primitive


class RangePointType(Enum):
    EXCLUSIVE = 1
    INCLUSIVE = 2

    @classmethod
    def is_inclusive(cls, inclusive: bool) -> "RangePointType":
        if inclusive:
            return cls.INCLUSIVE
        return cls.EXCLUSIVE


@dataclass
class RangePoint[T: (int, float)]:
    point: T
    type: RangePointType = RangePointType.INCLUSIVE


@dataclass
class Range[T: (int, float)]:
    min: RangePoint[T] | None = None
    max: RangePoint[T] | None = None


class ISchemaTest(ABC):
    @abstractmethod
    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        """validate"""
