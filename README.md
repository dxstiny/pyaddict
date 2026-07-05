# pyaddict

[![PyPI version](https://badge.fury.io/py/pyaddict.svg)](https://badge.fury.io/py/pyaddict)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pyaddict.svg)](https://pypi.python.org/pypi/pyaddict/)
[![PyPI license](https://img.shields.io/pypi/l/pyaddict.svg)](https://pypi.python.org/pypi/pyaddict/)

## Description
Yet another python library to safely work with json data. It implements many useful features such as optional chaining, schema validation, type casting, safe indexing and default values.

## Installation
```bash
pip install pyaddict
```

## Usage

### Accessing json data

```python
from pyaddict import JDict

data = {
    "name": "John",
    "age": 30,
    "cars": [
        {"model": "BMW 230", "mpg": 27.5},
        {"model": "Ford Edge", "mpg": 24.1}
    ]
}

jdict = JDict(data).chain()  # enable chaining

jdict.expect("name", str)  # "John"
jdict.expect("name", int)  # TypeError: name is str, not int
jdict.expect("address", str)  # KeyError: key 'address' not found
jdict.expect("cars[0].mpg", float)  # 27.5 (because we enabled chaining)

# if we prefer None
jdict.optional_get("name", str)  # "John"
jdict.optional_get("name", int)  # None
jdict.optional_get("address", str)  # None
jdict.optional_get("address.street", str)  # KeyError: address not found
jdict.optional_get("address?.street", str)  # None
jdict.optional_get("cars[2].mpg", str)  # IndexError: out of range
jdict.optional_get("cars[2]?.mpg", str)  # None

# if we don't care whether it exists or not
jdict.ensure("name", str)  # "John"
jdict.ensure("name", int)  # 0, because name is not an int
jdict.ensure("age", int)  # 30
jdict.ensure("age", str)  # "", because age is not a string
jdict.ensure("address", str, "moon")  # "moon"
jdict.ensure("cars[].model", list)  # [ "BMW 230", "Ford Edge" ]
jdict.ensure("cars[0].mpg", float)  # 27.5
jdict.ensure("cars[0].mpg", int)  # 0, because cars[0].model is not an int

# or cast to the desired type
jdict.ensure_cast("cars[0].mpg", int) # 27
```

Similar rules apply when working with lists:
```py
from pyaddict import JList

data = [{"name": "John", "age": 20}, {"name": "Jane", "age": 22}]

jlist = JList(data)

jlist.expect(0, dict)  # {"name": "John", "age": 20}
jlist.expect(0, int)  # TypeError: item is dict, not int
jlist.expect(2, dict)  # IndexError: out of range
jlist.expect("0.name", str)  # ValueError: invalid int

# if we enable chaining:
jlist = JList(data).chain()
jlist.expect("0.name", str)  # "John"
jlist.expect("[].name", list)  # ["John", "Jane"]
```

### Validating json data
```py
from pyaddict.schema import Anything, Array, Integer, Object, OneOf, String

schema = Object({
    "name": String(),
    "age": Integer().coerce(),
    "dogs": Array(
        OneOf(
            String(),
            Object({}, additional_properties=True)
        )
    ).min(1).optional(),
    "wildcard": Anything(),
    "valid": True
})

result = schema.validate({
    "name": "John",
    "age": 20.0,
    "wildcard": [1, 2, 3],
    "valid": True
})
result.valid  # True
result.unwrap()  # { "name": "John", "age": 20, "wildcard": [1, 2, 3], "valid": True }

result = schema.validate({
    "name": "John",
    "age": 5,
    "dogs": 1,
    "wildcard": True,
    "valid": True
})
result.valid  # False
result.unwrap()  # ValueError (invalid)
result.error  # 'dogs' should be list, not int
```

The library is fully typed and thus can be used with mypy & pylint. Check out the [wiki](https://github.com/dxstiny/pyaddict/wiki) for more information.

## License
[MIT](LICENSE)

## Author
[dxstiny](https://github.com/dxstiny)
