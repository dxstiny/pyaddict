from pyaddict.schema import (
    Anything,
    Array,
    Boolean,
    Float,
    Integer,
    Object,
    OneOf,
    String,
)

schema = Object(
    {
        "a": "b",
        "c": String(),
        "d": Array(Integer()),
        "e": Anything(),
        "f": Float(),
        "g": OneOf(Boolean(), Integer()),
    }
)

assert schema.validate(
    {
        "a": "b",
        "c": "hello, world",
        "d": [1, 2],
        "e": {"test": 123},
        "f": 1.0,
        "g": True,
    }
)
