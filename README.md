# pyaddict

[![PyPI version](https://badge.fury.io/py/pyaddict.svg)](https://badge.fury.io/py/pyaddict)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pyaddict.svg)](https://pypi.python.org/pypi/pyaddict/)
[![PyPI license](https://img.shields.io/pypi/l/pyaddict.svg)](https://pypi.python.org/pypi/pyaddict/)

## Description
Yet another python library to safely work with json data. It implements many useful features such as default values, type casting and safe indexing.

## Installation
```bash
pip install pyaddict
```

## Usage
```python
from pyaddict import JDict, JList

jdict = JDict({
    "name": "John",
    "age": 30,
    "cars": [
        {"model": "BMW 230", "mpg": 27.5},
        {"model": "Ford Edge", "mpg": 24.1}
    ]
})

# Get value
print(jdict.ensureCast("name", str))  # John
print(jdict.ensureCast("age", int))  # 30
print(jdict.ensureCast("age", str))  # "30"
print(jdict.optionalGet("age", str)) # None
print(jdict.tryGet("age", str))  # "30"
print(jdict.optionalGet("gender", str)) # None
print(jdict.tryGet("gender", str)) # None
print(jdict.ensure("gender", str)) # ""

cars = jdict.ensureCast("cars", JList)
print(cars.ensureCast(0, JDict).ensureCast("mpg", str))  # "27.5"
print(cars.ensureCast(1, JDict).ensureCast("mpg", str))  # "24.1"
print(cars.ensureCast(2, JDict).ensureCast("mpg", str))  # ""

print(cars.ensureCast(2, JDict).optionalGet("mpg", str))  # None
print(cars.assertGet(2, JDict))  # AssertionError
```

The library is fully typed and thus can be used with mypy & pylint. Check out the [wiki](https://github.com/dxstiny/pyaddict/wiki) for more information.

## When to use
When working with json data, it is common to have to deal with missing keys, wrong types, etc. This library provides a simple way to deal with these issues. Additionally, it provides easy-to-use typing support for mypy and pylint and detailed documentation.

## License
[MIT](LICENSE)

## Author
[dxstiny](https://github.com/dxstiny)
