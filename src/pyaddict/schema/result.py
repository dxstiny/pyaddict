"""Validation result helpers."""

from __future__ import annotations

from enum import Enum
from typing import Generic, List, Optional, TypeVar, cast

T = TypeVar("T")
U = TypeVar("U")


class ValidationState(Enum):

    """Validation state."""

    Valid = 0
    Invalid = 1


class ValidationError(ValueError):

    """Validation error."""

    __slots__ = ("_message", "_path", "_validation", "_cause")

    def __init__(
        self,
        message: str,
        path: List[str],
        validation: str,
        cause: List[ValidationError] | None = None,
    ) -> None:
        """Create new validation error."""
        super().__init__(message)
        self._message = message
        self._path = path
        self._validation = validation
        self._cause = cause or []

    def __repr__(self) -> str:
        """
        Return string representation.

        Returns:
            String representation.

        """
        return f"ValidationError({self})"

    def __str__(self) -> str:
        """
        Return friendly string.

        Returns:
            Friendly string.

        """
        result = f"{self._message} at {self.formatted_path}"
        if self._cause:
            result += ": \n"
            result += ",\n".join([f"\t- {x}" for x in self._cause])
        return result

    @property
    def formatted_path(self) -> str:
        """A friendly error path."""
        if len(self._path) == 0:
            return "(root): " + self._validation
        path = [str(p) for p in self._path]
        return ".".join(path) + ": " + self._validation

    @property
    def path(self) -> List[str]:
        """The path to the error."""
        return self._path

    @property
    def message(self) -> str:
        """The error message."""
        return self._message

    @property
    def validation(self) -> str:
        """The validation that failed."""
        return self._validation

    @property
    def cause(self) -> List[ValidationError]:
        """Contained errors used to trace."""
        return self._cause

    @staticmethod
    def inherit(error: Optional[ValidationError], path: List[str]) -> ValidationError:
        """
        Inherit a ValidationError (combines the paths).

        Returns:
            Inherited validation error

        """
        assert error is not None
        return ValidationError(
            error.message, path + error.path, error.validation, error.cause
        )


class ValidationResult(Generic[T]):

    """Validation result wrapper."""

    __slots__ = ("_state", "_data", "_error", "_nullable")

    def __init__(
        self,
        state: ValidationState,
        data: Optional[T] = None,
        error: Optional[ValidationError] = None,
        nullable: bool = False,
    ) -> None:
        """Create new validation result object."""
        self._state = state
        self._data = data
        self._error = error
        self._nullable = nullable

    @property
    def valid(self) -> bool:
        """If the value is valid."""
        return self._state == ValidationState.Valid

    def __bool__(self) -> bool:
        """
        If the value is valid.

        Returns:
            self.valid

        """
        return self.valid

    def __repr__(self) -> str:
        """
        Return the string representation.

        Returns:
            String representation.

        """
        if self._state == ValidationState.Valid:
            return f"ValidationResult({self._data})"
        return f"ValidationResult({self._error})"

    def _assert_return_data(self) -> T:
        if not self._nullable:
            assert self._data is not None
        return cast(T, self._data)

    def unwrap(self) -> T:
        """
        Unwrap the value if valid, otherwise raise an error.

        Returns:
            The validated value.

        Raises:
            AssertionError: if the value is None.
            ValueError: if invalid.

        """
        if self._state == ValidationState.Valid:
            return self._assert_return_data()
        raise ValueError("unwrap called on invalid value")

    def unwrap_or(self, default: T) -> T:
        """
        Unwrap the value if valid, otherwise return the default.

        Returns:
            The validated value.
            default: if invalid.

        Raises:
            AssertionError: if the value is None.

        """
        if self._state == ValidationState.Valid:
            return self._assert_return_data()
        return default

    def expect(self, msg: Optional[str] = None) -> T:
        """
        Unwrap the value if valid.

        Returns:
            The validated value.

        Raises:
            ValidationError: if the validation failed.
            ValueError: if a message is provided.

        """
        if self._state == ValidationState.Valid:
            return self._assert_return_data()
        if msg is None:
            assert self._error is not None
            raise self._error
        raise ValueError(msg)

    @property
    def error(self) -> ValidationError | None:
        """The error, if invalid."""
        return self._error

    @property
    def value(self) -> T | None:
        """The value, if valid."""
        return self._data

    def invalidate(self, error: Optional[ValidationError] = None) -> None:
        """Invalidate the value."""
        self._state = ValidationState.Invalid
        self._error = error

    def update(self, value: ValidationResult[T]) -> ValidationResult[T]:
        """
        Update the value, invalidating if necessary.

        Returns:
            :return: updated validation result (self)

        """
        if not value:
            self.invalidate(value.error)
        else:
            self._data = value.unwrap()
        return self

    @staticmethod
    def ok(data: U, nullable: bool = False) -> ValidationResult[U]:
        """
        Create a valid result.

        Returns:
            Validation result with the error.

        """
        return ValidationResult(ValidationState.Valid, data=data, nullable=nullable)

    @staticmethod
    def err(error: Optional[ValidationError] = None) -> ValidationResult[U]:
        """
        Create an invalid result.

        Returns:
            Validation result with the error.

        """
        return ValidationResult(ValidationState.Invalid, error=error)
