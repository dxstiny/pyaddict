"""Schema base helpers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

from pyaddict.schema.result import ValidationError, ValidationResult


class ISchemaType[C, T](ABC):
    """Abstract schema base."""

    def __init__(self) -> None:
        """Create new schema definition."""
        self._default: T | None = None
        self._coerce: bool = False
        self._nullable: bool = False
        self._optional: bool = False

    def coerce(self) -> C:
        """
        Allow value coercion (e.g., str -> int).

        Returns:
            self.

        """
        self._coerce = True
        return cast(C, self)

    def default(self, value: T) -> C:
        """
        Set a default value for the validated object, if the data is null or missing.

        Use in combination with `.nullable()` and/or `.optional()`.

        Returns:
            self.

        """
        self._default = value
        return cast(C, self)

    def optional(self) -> C:
        """
        Allow the property to be missing.

        Use `.default()` to set a default value for the result.

        Returns:
            self.

        """
        self._optional = True
        return cast(C, self)

    @property
    def default_value(self) -> T | None:
        """
        Default value, if one is set.

        Returns:
            self.

        """
        return self._default

    @property
    def is_optional(self) -> bool:
        """
        Whether the property is optional.

        Returns:
            self.

        """
        return self._optional

    @abstractmethod
    def nullable(self) -> Any:
        """
        Allow the property to be None/null.

        Use `.default()` to set a default value for the result.

        Returns:
            self.

        """
        self._nullable = True
        return self

    @abstractmethod
    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[Any]:
        """
        Validate the provided value.

        Returns:
            ValidationResult.

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
Validatable = SchemaType | Primitive | None


class RangePointType(Enum):
    """Range point type."""

    EXCLUSIVE = 1
    INCLUSIVE = 2

    @classmethod
    def is_inclusive(cls, inclusive: bool) -> "RangePointType":
        """
        Create from boolean.

        Returns:
            RangePointType.

        """
        if inclusive:
            return cls.INCLUSIVE
        return cls.EXCLUSIVE


@dataclass
class RangePoint[T: (int, float)]:
    """Range point definition."""

    point: T
    type: RangePointType = RangePointType.INCLUSIVE


@dataclass
class Range[T: (int, float)]:
    """Range specification."""

    min: RangePoint[T] | None = None
    max: RangePoint[T] | None = None


class ISchemaTest(ABC):
    """Abstract base for validation tests."""

    @abstractmethod
    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        """
        Validate.

        Returns:
            ValidationResult.

        """
