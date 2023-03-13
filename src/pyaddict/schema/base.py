"""json schema validation inspired by zod"""
from __future__ import annotations
from typing import List, Optional, Generic,TypeVar, Any, Type
from abc import ABC, abstractmethod
import json

from .result import ValidationResult, ValidationError


T = TypeVar("T")
U = TypeVar("U")
IS = TypeVar("IS", bound="ISchemaType[Any]")


class INullable(Generic[IS]):
    """Nullable"""
    def __init__(self) -> None:
        super().__init__()
        self._nullable: bool = False

    def nullable(self) -> IS:
        """make the value nullable"""
        self._nullable = True
        return self # type: ignore


class ISchemaType(ABC, Generic[IS], INullable[IS]):
    """Schema Type"""
    def __init__(self) -> None:
        super().__init__()
        self._optional: bool = False
        self._coerce: bool = False
        self._default: Optional[Any] = None

    def coerce(self) -> IS:
        """coerce the value (float -> int, str -> bool, etc.)"""
        self._coerce = True
        return self # type: ignore

    def optional(self) -> IS:
        """make the value optional"""
        self._optional = True
        self._nullable = True
        return self # type: ignore

    def default(self, value: T) -> IS:
        """set the default value"""
        self._default = value
        self._nullable = True
        return self # type: ignore

    @abstractmethod
    def validate(self, value: T) -> ValidationResult[T]:
        """
        validates the value

        returns a ValidationResult,
        which contains an error if the value is invalid
        or the value if valid
        """
        return ValidationResult.ok(value)

    def _coerceValue(self, value: Any, to: Type[T]) -> ValidationResult[T]:
        """coerce the value"""
        if self._nullable and value is None:
            return ValidationResult.ok( self._default, True ) # type: ignore

        if not self._coerce:
            if isinstance(value, to):
                return ValidationResult.ok( value )
            return ValidationResult.err( ValidationError(f"{value} is not of type {to}",
                                                         [], "coerce") )

        # str -> bool
        if to == bool and isinstance(value, str):
            if value.lower() in ("true", "1", "yes", "y"):
                return ValidationResult.ok( True ) # type: ignore
            if value.lower() in ("false", "0", "no", "n"):
                return ValidationResult.ok( False ) # type: ignore
            return ValidationResult.err(
                ValidationError(f"{value} is not a boolean",
                                [],
                                "coerce"))

        # str -> dict
        if to in (dict, list) and isinstance(value, str): # type: ignore # (comparison-overlap)
            return ValidationResult.ok( json.loads(value) )

        # * -> * (hope & pray)
        return ValidationResult.ok( to(value) ) # type: ignore

    def __call__(self, value: T) -> T:
        """
        expect the value to be valid,
        otherwise raise an error
        """
        return self.expect(value)

    def expect(self, value: T, msg: Optional[str] = None) -> T:
        """
        expect the value to be valid,
        otherwise raise an error with the message, if provided,
        otherwise raise the original error
        """
        return self.validate(value).expect(msg)

    def error(self, value: T) -> Optional[ValidationError]:
        """
        get the error if the value is invalid,
        otherwise return None
        """
        return self.validate(value).error

    def valid(self, value: T) -> bool:
        """
        is the value valid?
        """
        return self.validate(value).valid()


class IWithEnum(ABC, Generic[T, IS], INullable[IS]):
    """Schema Type with Enum"""

    def __init__(self) -> None:
        super().__init__()
        self._enum: Optional[List[T]] = None

    def validate(self, value: T) -> ValidationResult[T]:
        """validate the value"""
        if not self._enum:
            return ValidationResult.ok(value)

        if self._nullable and value is None:
            return ValidationResult.ok( value, True ) # type: ignore

        if value not in self._enum:
            return ValidationResult.err(
                ValidationError(f"{value} is not in {self._enum}",
                                [],
                                "enum"))
        return ValidationResult.ok(value)

    def enum(self, *values: U) -> IS:
        """set the enum values"""
        self._enum = list(values) # type: ignore
        return self # type: ignore


class IWithLength(ABC, Generic[T, IS], INullable[IS]):
    """Schema Type with Length (array, string, etc.)"""
    def __init__(self) -> None:
        super().__init__()
        self._min: Optional[int] = None
        self._max: Optional[int] = None
        self._minInclusive: bool = False
        self._maxInclusive: bool = False

    @abstractmethod
    def length(self, value: Any) -> int:
        """get the length of the value"""

    def validate(self, value: T) -> ValidationResult[T]:
        """validate the value"""
        if self._nullable and value is None:
            return ValidationResult.ok( value, True ) # type: ignore

        if self._min is not None:
            length = self.length(value)

            if self._minInclusive:
                if length < self._min:
                    return ValidationResult.err(
                        ValidationError(f"expected {self.length(value)} to be greater than or equal to {self._min}", # pylint: disable=line-too-long
                                        [],
                                        "min"))
            else:
                if length <= self._min:
                    return ValidationResult.err(
                        ValidationError(f"expected {self.length(value)} to be greater than {self._min}", # pylint: disable=line-too-long
                                        [],
                                        "min"))
        if self._max is not None:
            length = self.length(value)

            if self._maxInclusive:
                if length > self._max:
                    return ValidationResult.err(
                        ValidationError(f"expected {self.length(value)} to be less than or equal to {self._max}", # pylint: disable=line-too-long
                                        [],
                                        "max"))
            else:
                if length >= self._max:
                    return ValidationResult.err(
                        ValidationError(f"expected {self.length(value)} to be less than {self._max}", # pylint: disable=line-too-long
                                        [],
                                        "max"))
        return ValidationResult.ok(value)

    def min(self, min_: int, inclusive: bool = True) -> IS:
        """set the min length"""
        self._min = min_
        self._minInclusive = inclusive
        return self # type: ignore

    def max(self, max_: int, inclusive: bool = True) -> IS:
        """set the max length"""
        self._max = max_
        self._maxInclusive = inclusive
        return self # type: ignore
