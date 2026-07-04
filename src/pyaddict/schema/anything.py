from typing import Any

from pyaddict.schema.base import ISchemaType
from pyaddict.schema.result import ValidationResult


class Anything(ISchemaType["Anything", Any | None]):
    def nullable(self) -> Any:
        return self

    def validate(
        self, value: Any | None, *, path: list[str] | None = None
    ) -> ValidationResult[Any | None]:
        return ValidationResult.ok(value)
