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
```python
from pyaddict import JDict, JList
from pyaddict.schema import Object, String, Integer, Array

jdict = JDict({
    "name": "John",
    "age": 30,
    "cars": [
        {"model": "BMW 230", "mpg": 27.5},
        {"model": "Ford Edge", "mpg": 24.1}
    ]
})

# dicts
print(jdict.ensure("name", str))  # John
print(jdict.ensure("age", int))  # 30
print(jdict.ensure("age", str))  # ""
print(jdict.ensureCast("age", str))  # "30"
print(jdict.optionalGet("age", str)) # None
print(jdict.optionalCast("age", str))  # "30"
print(jdict.optionalGet("gender", str)) # None
print(jdict.optionalCast("gender", str)) # None
print(jdict.ensure("gender", str)) # ""

# lists
cars = jdict.ensureCast("cars", JList)
print(cars.assertGet(1, dict))  # {'model': 'Ford Edge', 'mpg': 24.1}
print(cars.assertGet(2, dict))  # AssertionError

# iterators
for car in cars.iterator().ensureCast(JDict):
    print(car.ensureCast("model", str)) # BMW 230, Ford Edge

# chaining
chain = jdict.chain()
print(chain.ensureCast("cars[1].mpg", str))  # "24.1"
print(chain.ensureCast("cars[2].mpg", str))  # ""
# or via direct access (returns Optional[Any]!)
print(chain["cars[2].mpg"])  # IndexError
print(chain["cars[2]?.mpg"])  # None

# schema validation
schema = Object({
    "name": String(),
    "age": String().coerce(),
    "dogs": Array(String()).min(1).optional()
}).withAdditionalProperties()
print(schema.error(jdict)) # None

badSchema = Object({
    "name": String().min(5),
    "age": Float(),
    "cars": Object()
})
print(badSchema.error(jdict)) # ValidationError(expected 4 to be greater than or equal to 5, name: min)

staticSchema = Object({
    "name": "John",
    "age": 30,
    "cars": [
        {"model": "BMW 230", "mpg": 27.5},
        {"model": "Ford Edge", "mpg": 24.1}
    ]
})
print(staticSchema.error(jdict)) # None

mixedSchema = Object({
    "name": String().enum("John"),
    "age": 30,
    "dogs": Array(String()).min(1).optional()
}).withAdditionalProperties()
print(mixedSchema.error(jdict)) # None
```

The library is fully typed and thus can be used with mypy & pylint. Check out the [wiki](https://github.com/dxstiny/pyaddict/wiki) for more information.

## When to use
When working with json data, it is common to have to deal with missing keys, wrong types, etc. This library provides a simple way to deal with these issues. Additionally, it provides easy-to-use typing support for mypy and pylint and detailed documentation.
Starting with version 1.0.0, pyaddict includes a schema validation feature inspired by [zod](https://github.com/colinhacks/zod). It is especially useful when validating user input, e.g. in web applications.

## License
[MIT](LICENSE)

## Author
[dxstiny](https://github.com/dxstiny)
