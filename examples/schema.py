from pyaddict.schema import Object, String, Integer, Array, Float

dict = {
    "name": "John",
    "age": 30,
    "cars": [
        {"model": "BMW 230", "mpg": 27.5},
        {"model": "Ford Edge", "mpg": 24.1}
    ]
}

schema = Object({
    "name": String(),
    "age": Integer(),
    "cars": Array(Object({
        "model": String(),
        "mpg": Float()
    })).min(1, False).max(2)
})

print(schema.error(dict)) # None

schema = Object({
    "name": String(),
    "age": String().coerce(),
    "dogs": Array(String()).min(1).optional()
}).withAdditionalProperties()

print(schema.error(dict)) # None

badSchema = Object({
    "name": String().min(5),
    "age": Float(),
    "cars": Object()
})

print(badSchema.error(dict)) # ValidationError(expected 4 to be greater than or equal to 5, name: min)