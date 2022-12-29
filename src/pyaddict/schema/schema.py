"""json schema validation inspired by zod"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, TypeVar, Pattern, Generic, Union, Type
from abc import ABC, abstractmethod
import re
import json
from enum import Enum

from pyaddict.types import JObject


T = TypeVar("T")
U = TypeVar("U")
IS = TypeVar("IS")


class ValidationState(Enum):
    """ValidationState"""
    Valid = 0
    Invalid = 1


class ValidationError(ValueError):
    """ValidationError"""
    def __init__(self,
                 message: str,
                 path: List[str],
                 validation: str) -> None:
        super().__init__(message)
        self._message = message
        self._path = path
        self._validation = validation

    def __repr__(self) -> str:
        return f"ValidationError({self._message}, {self.formattedPath})"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def formattedPath(self) -> str:
        """a friendly path for the error"""
        if len(self._path) == 0:
            return '(root): ' + self._validation
        path = [ str(p) for p in self._path ]
        return '.'.join(path) + ': ' + self._validation

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

    @staticmethod
    def inherit(error: Optional[ValidationError], path: List[str]) -> ValidationError:
        """inherit a ValidationError (combines the paths)"""
        assert error is not None
        return ValidationError(error.message, path + error.path, error.validation)


class ValidationResult(Generic[T]):
    """OptionalData"""
    def __init__(self,
                 state: ValidationState,
                 data: Optional[T] = None,
                 error: Optional[ValidationError] = None) -> None:
        self._state = state
        self._data = data
        self._error = error

    def valid(self) -> bool:
        """is the value valid?"""
        return self._state == ValidationState.Valid

    def __bool__(self) -> bool:
        return self.valid()

    def __repr__(self) -> str:
        if self._state == ValidationState.Valid:
            return f"ValidationResult({self._data})"
        return f"ValidationResult({self._error})"

    def unwrap(self) -> T:
        """unwrap the value if valid, otherwise raise an error"""
        if self._state == ValidationState.Valid:
            assert self._data is not None
            return self._data
        raise ValueError("unwrap called on invalid value")

    def unwrapOr(self, default: T) -> T:
        """unwrap the value if valid, otherwise return the default"""
        if self._state == ValidationState.Valid:
            assert self._data is not None
            return self._data
        return default

    def expect(self, msg: Optional[str] = None) -> T:
        """
        unwrap the value if valid,
        otherwise raise an error with the message, if provided,
        otherwise raise the original error
        """
        if self._state == ValidationState.Valid:
            assert self._data is not None
            return self._data
        if msg is None:
            assert self._error is not None
            raise self._error # pylint: disable=raising-bad-type # (mypy bug)
        raise ValueError(msg)

    @property
    def error(self) -> Optional[ValidationError]:
        """the error if invalid"""
        return self._error

    def invalidate(self, error: Optional[ValidationError] = None) -> None:
        """invalidate the value"""
        self._state = ValidationState.Invalid
        self._error = error

    def update(self, value: ValidationResult[T]) -> None:
        """update the value"""
        if not value:
            self.invalidate(value.error)

    @staticmethod
    def ok(data: U) -> ValidationResult[U]:
        """create a valid result"""
        return ValidationResult(ValidationState.Valid, data=data)

    @staticmethod
    def err(error: Optional[ValidationError] = None) -> ValidationResult[U]:
        """create an invalid result"""
        return ValidationResult(ValidationState.Invalid, error=error)


class ISchemaType(ABC, Generic[IS]):
    """Schema Type"""
    def __init__(self) -> None:
        super().__init__()
        self._min: Optional[int] = None
        self._max: Optional[int] = None
        self._optional: bool = False
        self._coerce: bool = False

    def coerce(self) -> IS:
        """coerce the value (float -> int, str -> bool, etc.)"""
        self._coerce = True
        return self # type: ignore

    def optional(self) -> IS:
        """make the value optional"""
        self._optional = True
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
        if self._coerce:
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
        if not isinstance(value, to):
            return ValidationResult.err( ValidationError(f"{value} is not of type {to}",
                                                         [], "coerce") )
        return ValidationResult.ok( value )

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


class IWithEnum(ABC, Generic[T, IS]):
    """Schema Type with Enum"""
    def __init__(self) -> None:
        super().__init__()
        self._enum: Optional[List[T]] = None

    def validate(self, value: T) -> ValidationResult[T]:
        """validate the value"""
        if self._enum is not None and value not in self._enum:
            return ValidationResult.err(
                ValidationError(f"{value} is not in {self._enum}",
                                [],
                                "enum"))
        return ValidationResult.ok(value)

    def enum(self, *values: U) -> IS:
        """set the enum values"""
        self._enum = list(*values)
        return self # type: ignore


class IWithLength(ABC, Generic[T, IS]):
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
        length = self.length(value)
        if self._min is not None:
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


class String(ISchemaType["String"], IWithLength[str, "String"], IWithEnum[str, "String"]):
    """String Schema Type"""
    def __init__(self) -> None:
        super().__init__()
        self._regex: Optional[Union[Pattern[str], str]] = None
        self._regexType: Optional[str] = None
        self._regexMessage: Optional[str] = None

    def length(self, value: str) -> int:
        return len(value)

    def validate(self, value: Any) -> ValidationResult[str]:
        result = self._coerceValue(value, str)

        if not result:
            return result

        result.update(IWithEnum.validate(self, result.unwrap()))
        if not result:
            return result

        result.update(IWithLength.validate(self, result.unwrap()))
        if not result:
            return result

        if self._regex is not None:
            if isinstance(self._regex, str):
                self._regex = re.compile(self._regex)
            if not self._regex.match(result.unwrap()):
                assert self._regexType is not None and self._regexMessage is not None
                result.invalidate(
                    ValidationError(self._regexMessage, [], self._regexType))
        return result

    def regex(self, regex: Union[str, Pattern[str]]) -> String:
        """validate the value against a regex"""
        self._regex = regex
        self._regexType = "regex"
        self._regexMessage = f"string didn't match {self._regex}"
        return self

    def email(self) -> String:
        """validate the value as an email"""
        self._regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        self._regexType = "email"
        self._regexMessage = "string is not a valid email"
        return self

    def url(self) -> String:
        """validate the value as a url"""
        self._regex = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
        self._regexType = "url"
        self._regexMessage = "string is not a valid url"
        return self


class Integer(ISchemaType["Integer"], IWithEnum[int, "Integer"], IWithLength[int, "Integer"]):
    """Integer Schema Type"""
    def validate(self, value: Any) -> ValidationResult[int]:
        result = self._coerceValue(value, int)
        if not result:
            return result

        result.update(IWithEnum.validate(self, result.unwrap()))
        if not result:
            return result

        result.update(IWithLength.validate(self, result.unwrap()))
        return result

    def length(self, value: int) -> int:
        return value


class Float(ISchemaType["Float"], IWithEnum[float, "Float"], IWithLength[float, "Float"]):
    """Float Schema Type"""
    def validate(self, value: Any) -> ValidationResult[float]:
        result = self._coerceValue(value, float)
        if not result:
            return result

        result.update(IWithEnum.validate(self, value))
        if not result:
            return result

        result.update(IWithLength.validate(self, value))
        return result

    def length(self, value: float) -> float:
        return value


class Boolean(ISchemaType["Boolean"], IWithEnum[bool, "Boolean"]):
    """Boolean Schema Type"""
    def validate(self, value: Any) -> ValidationResult[bool]:
        result = self._coerceValue(value, bool)
        if not result:
            return result
        result.update(IWithEnum.validate(self, value))
        return result


class Object(ISchemaType["Object"]):
    """Object Schema Type"""
    def __init__(self,
                 body: Optional[Dict[str, ISchemaType[Any]]] = None,
                 additionalProperties: bool = False) -> None:
        super().__init__()
        self._body = body
        self._allowAdditionalProperties = additionalProperties

    def withAdditionalProperties(self, withAdditionalProperties: bool = True) -> Object:
        """disallow additional properties"""
        self._allowAdditionalProperties = withAdditionalProperties
        return self

    def validate(self, value: Any) -> ValidationResult[JObject]:
        result = self._coerceValue(value, dict)
        if not result:
            return result

        body = self._body or {}

        for key, schema in body.items():
            if key not in result.unwrap():
                if not schema._optional: # pylint: disable=protected-access
                    result.invalidate(
                        ValidationError(f"expected {key} to be present",
                                        [],
                                        "required"))
                    return result
                continue
            keyRes = schema.validate(value[key])
            if not keyRes:
                result.invalidate(ValidationError.inherit(keyRes.error, [key]))
                return result
            value[key] = keyRes.unwrap()

        if not self._allowAdditionalProperties:
            for key in result.unwrap():
                if key not in body:
                    result.invalidate(ValidationError(f"unexpected property {key}",
                                                     [],
                                                     "additionalProperties"))
                    return result

        return result

class Array(ISchemaType["Array"], IWithLength[List[Any], "Array"]):
    """Array Schema Type"""
    def __init__(self, item: ISchemaType[Any]) -> None:
        super().__init__()
        self._item = item

    def validate(self, value: Any) -> ValidationResult[List[Any]]:
        result = self._coerceValue(value, list)
        if not result:
            return result

        result.update(IWithLength.validate(self, result.unwrap()))
        if not result:
            return result

        values: List[Any] = [ ]
        for item in result.unwrap():
            res = self._item.validate(item)
            if not res.valid():
                result.invalidate(ValidationError.inherit(res.error, ["[]"]))
                return result
            values.append(res.unwrap())
        return ValidationResult.ok(values)

    def length(self, value: List[Any]) -> int:
        return len(value)
