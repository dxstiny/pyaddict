import json
from typing import Any, cast

from pyaddict.schema.base import (
    ISchemaTest,
    ISchemaType,
    Validatable,
)
from pyaddict.schema.common import validate
from pyaddict.schema.result import ValidationError, ValidationResult


class CoerceObjectTest(ISchemaTest):
    def __init__(self, coerce: bool) -> None:
        super().__init__()
        self._coerce = coerce

    def test[T](self, val: T, path: list[str]) -> ValidationResult[T]:
        value: Any = val

        if not self._coerce:
            if not isinstance(value, dict):
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) is not of type dict", path, "coerce"
                    )
                )
        elif not isinstance(value, dict):
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            if not isinstance(value, dict):
                return ValidationResult.err(
                    ValidationError(
                        f"{val} ({type(val)}) cannot be cast to type dict",
                        path,
                        "coerce",
                    )
                )
        return ValidationResult.ok(cast(T, value))


class _Object[R](ISchemaType["_Object[R]", R]):
    def __init__(
        self,
        body: dict[str, Validatable] | None = None,
        *,
        additional_properties: bool = False,
    ) -> None:
        super().__init__()
        self._body = body or {}
        self._additional_properties = additional_properties

    def with_additional_properties(self) -> "_Object[R]":
        self._additional_properties = True
        return self

    def nullable(self) -> "_Object[dict[str, Any] | None]":
        return cast(OptionalObject, super().nullable())

    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[R]:
        path = path or []

        result = self._test_nullable(value, path)

        if not result or result.value is None:
            return cast(ValidationResult[R], result)

        for test in [CoerceObjectTest(self._coerce)]:
            result.update(test.test(result.unwrap_or(value), path))

        if isinstance(value, dict):
            failed: list[ValidationError] = []

            all_keys = set([*value.keys(), *self._body.keys()])

            result_dict: dict[str, Any] = {}

            for key in all_keys:
                if key not in self._body.keys():
                    if not self._additional_properties:
                        failed.append(
                            ValidationError(
                                f"unexpected property {key}",
                                path,
                                "additional_properties",
                            )
                        )
                    else:
                        result_dict[key] = value[key]
                    continue

                schema = self._body[key]

                if (
                    isinstance(schema, ISchemaType)
                    and schema.is_optional
                    and key not in value.keys()
                ):
                    if schema.default_value:
                        result_dict[key] = schema.default_value
                    continue

                if key not in value.keys():
                    failed.append(
                        ValidationError(
                            f"expected {key} to be present", path, "required"
                        )
                    )
                    continue

                item = value[key]
                item_result = validate(
                    item,
                    schema,
                    path=[*path, key],
                )
                if item_result and item_result.value:
                    result_dict[key] = item_result.value
                if not item_result and item_result.error:
                    failed.append(item_result.error)

            if failed:
                result.invalidate(
                    error=ValidationError(
                        "items do not match schema", path, "schema", cause=failed
                    )
                )

            result.update(ValidationResult.ok(result_dict))

        return cast(ValidationResult[R], result)

    def __getitem__(self, key: str) -> Validatable:
        return self._body[key]

    def __setitem__(self, key: str, schema: Validatable) -> Validatable | None:
        self._body[key] = schema

    def __delitem__(self, key: str) -> None:
        del self._body[key]


Object = _Object[dict[str, Any]]
OptionalObject = _Object[dict[str, Any] | None]
