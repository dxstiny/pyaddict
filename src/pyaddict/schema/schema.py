"""json schema validation inspired by zod"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, TypeVar, Pattern, Union
import re

from pyaddict.types import JObject

from pyaddict.schema.result import ValidationResult, ValidationError
from pyaddict.schema.base import ISchemaType, IWithLength, IWithEnum


T = TypeVar("T")
U = TypeVar("U")
IS = TypeVar("IS", bound="ISchemaType[Any]")


class String(
    ISchemaType["String"], IWithLength[str, "String"], IWithEnum[str, "String"]
):
    """String Schema Type"""

    __slots__ = (
        "_regex",
        "_regexType",
        "_regexMessage",
        "_min",
        "_max",
        "_minInclusive",
        "_maxInclusive",
        "_enum",
        "_nullable",
        "_coerce",
        "_default",
        "_optional",
    )

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
                    ValidationError(self._regexMessage, [], self._regexType)
                )
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


class Integer(
    ISchemaType["Integer"], IWithEnum[int, "Integer"], IWithLength[int, "Integer"]
):
    """Integer Schema Type"""

    __slots__ = (
        "_min",
        "_max",
        "_minInclusive",
        "_maxInclusive",
        "_enum",
        "_nullable",
        "_coerce",
        "_default",
        "_optional",
    )

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


class Float(
    ISchemaType["Float"], IWithEnum[float, "Float"], IWithLength[float, "Float"]
):
    """Float Schema Type"""

    __slots__ = (
        "_min",
        "_max",
        "_minInclusive",
        "_maxInclusive",
        "_enum",
        "_nullable",
        "_coerce",
        "_default",
        "_optional",
    )

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

    __slots__ = ("_enum", "_nullable", "_coerce", "_default", "_optional")

    def validate(self, value: Any) -> ValidationResult[bool]:
        result = self._coerceValue(value, bool)
        if not result:
            return result
        result.update(IWithEnum.validate(self, value))
        return result


class Object(ISchemaType["Object"]):
    """Object Schema Type"""

    __slots__ = (
        "_body",
        "_allowAdditionalProperties",
        "_nullable",
        "_coerce",
        "_default",
        "_optional",
    )

    def __init__(
        self,
        body: Optional[Dict[str, ISchemaType[Any] | Any]] = None,
        additionalProperties: bool = False,
    ) -> None:
        super().__init__()
        self._body = body
        self._allowAdditionalProperties = additionalProperties

    def withAdditionalProperties(self, withAdditionalProperties: bool = True) -> Object:
        """disallow additional properties"""
        self._allowAdditionalProperties = withAdditionalProperties
        return self

    def validate(self, value: Any) -> ValidationResult[JObject]:
        result = self._coerceValue(value, dict)
        if value is None and self._nullable:
            return result
        if not result:
            return result

        resultDict: JObject = {}
        body = self._body or {}

        for key, schema in body.items():
            if key not in result.unwrap():
                if not isinstance(schema, ISchemaType) or not schema._optional:  # pylint: disable=protected-access
                    result.invalidate(
                        ValidationError(f"expected {key} to be present", [], "required")
                    )
                    return result
                continue

            if not isinstance(schema, ISchemaType):
                if value[key] != schema:
                    result.invalidate(
                        ValidationError(
                            f"expected {value[key]} to equal {schema}", [key], "equals"
                        )
                    )
                    return result
                continue

            keyRes = schema.validate(value[key])
            if not keyRes:
                result.invalidate(ValidationError.inherit(keyRes.error, [key]))
                return result
            resultDict[key] = keyRes.unwrap()

        if not self._allowAdditionalProperties:
            for key in result.unwrap():
                if key not in body:
                    result.invalidate(
                        ValidationError(
                            f"unexpected property {key}", [], "additionalProperties"
                        )
                    )
                    return result

        return result.update(ValidationResult.ok(resultDict))


class Array(ISchemaType["Array"], IWithLength[List[Any], "Array"]):
    """Array Schema Type"""

    __slots__ = ("_item", "_min", "_max", "_minInclusive", "_maxInclusive")

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

        values: List[Any] = []
        for item in result.unwrap():
            res = self._item.validate(item)
            if not res.valid():
                result.invalidate(ValidationError.inherit(res.error, ["[]"]))
                return result
            values.append(res.unwrap())
        return ValidationResult.ok(values)

    def length(self, value: List[Any]) -> int:
        return len(value)


class OneOf(ISchemaType["OneOf"]):
    """OneOf Schema Type"""

    __slots__ = ("_items", "_nullable", "_coerce", "_default", "_optional")

    def __init__(self, *items: ISchemaType[Any]) -> None:
        super().__init__()
        self._items = items

    def validate(self, value: Any) -> ValidationResult[Any]:
        errors: List[ValidationError] = []
        for item in self._items:
            res = item.validate(value)
            if res.valid():  # use typeguard
                return res
            assert res.error
            errors.append(res.error)
        return ValidationResult.err(
            ValidationError(
                "value didn't match any of the schemas", [], "oneOf", cause=errors
            )
        )
