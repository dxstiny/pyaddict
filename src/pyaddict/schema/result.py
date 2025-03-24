"""json schema validation inspired by zod"""

from __future__ import annotations
from typing import List, Optional, Generic, TypeVar, cast
from enum import Enum

T = TypeVar("T")
U = TypeVar("U")


class ValidationState(Enum):
    """ValidationState"""

    Valid = 0
    Invalid = 1


class ValidationError(ValueError):
    """ValidationError"""

    __slots__ = ("_message", "_path", "_validation", "_cause")

    def __init__(
        self,
        message: str,
        path: List[str],
        validation: str,
        cause: List[ValidationError] | None = None,
    ) -> None:
        super().__init__(message)
        self._message = message
        self._path = path
        self._validation = validation
        self._cause = cause or []

    def __repr__(self) -> str:
        return f"ValidationError({self})"

    def __str__(self) -> str:
        result = f"{self._message} at {self.formattedPath}"
        if self._cause:
            result += ": \n"
            result += ",\n".join([f"\t- {x}" for x in self._cause])
        return result

    @property
    def formattedPath(self) -> str:
        """a friendly path for the error"""
        if len(self._path) == 0:
            return "(root): " + self._validation
        path = [str(p) for p in self._path]
        return ".".join(path) + ": " + self._validation

    @property
    def path(self) -> List[str]:
        """the path to the error"""
        return self._path

    @property
    def message(self) -> str:
        """the error message"""
        return self._message

    @property
    def validation(self) -> str:
        """the validation that failed"""
        return self._validation

    @property
    def cause(self) -> List[ValidationError]:
        """conatined errors used to trace"""
        return self._cause

    @staticmethod
    def inherit(error: Optional[ValidationError], path: List[str]) -> ValidationError:
        """inherit a ValidationError (combines the paths)"""
        assert error is not None
        return ValidationError(
            error.message, path + error.path, error.validation, error.cause
        )


class ValidationResult(Generic[T]):
    """OptionalData"""

    __slots__ = ("_state", "_data", "_error", "_nullable")

    def __init__(
        self,
        state: ValidationState,
        data: Optional[T] = None,
        error: Optional[ValidationError] = None,
        nullable: bool = False,
    ) -> None:
        self._state = state
        self._data = data
        self._error = error
        self._nullable = nullable

    def valid(self) -> bool:
        """is the value valid?"""
        return self._state == ValidationState.Valid

    def __bool__(self) -> bool:
        return self.valid()

    def __repr__(self) -> str:
        if self._state == ValidationState.Valid:
            return f"ValidationResult({self._data})"
        return f"ValidationResult({self._error})"

    def _assertReturnData(self) -> T:
        if not self._nullable:
            assert self._data is not None
        return cast(T, self._data)

    def unwrap(self) -> T:
        """unwrap the value if valid, otherwise raise an error"""
        if self._state == ValidationState.Valid:
            return self._assertReturnData()
        raise ValueError("unwrap called on invalid value")

    def unwrapOr(self, default: T) -> T:
        """unwrap the value if valid, otherwise return the default"""
        if self._state == ValidationState.Valid:
            return self._assertReturnData()
        return default

    def expect(self, msg: Optional[str] = None) -> T:
        """
        unwrap the value if valid,
        otherwise raise an error with the message, if provided,
        otherwise raise the original error
        """
        if self._state == ValidationState.Valid:
            return self._assertReturnData()
        if msg is None:
            assert self._error is not None
            raise self._error
        raise ValueError(msg)

    @property
    def error(self) -> Optional[ValidationError]:
        """the error if invalid"""
        return self._error

    def invalidate(self, error: Optional[ValidationError] = None) -> None:
        """invalidate the value"""
        self._state = ValidationState.Invalid
        self._error = error

    def update(self, value: ValidationResult[T]) -> ValidationResult[T]:
        """update the value"""
        if not value:
            self.invalidate(value.error)
        else:
            self._data = value.unwrap()
        return self

    @staticmethod
    def ok(data: U, nullable: bool = False) -> ValidationResult[U]:
        """create a valid result"""
        return ValidationResult(ValidationState.Valid, data=data, nullable=nullable)

    @staticmethod
    def err(error: Optional[ValidationError] = None) -> ValidationResult[U]:
        """create an invalid result"""
        return ValidationResult(ValidationState.Invalid, error=error)
