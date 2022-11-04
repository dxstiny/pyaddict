from pyaddict.pyaddict import JDict, JList

adventurer = {
  "name": 'Alice',
  "cat": {
    "name": 'Dinah'
  },
  "animals": [{
    "name": 'Dinah',
    "type": 'cat'
  }, {
    "name": 'Rabbit',
    "type": 'bunny',
    "age": 2,
    "ages": "2"
  }]
}
chain = JDict(adventurer).chain()

print(chain.optionalGet("dog?.name", str)) # None
print(chain.optionalGet("pets?.[1]?.name", str)) # None

print(chain.optionalGet("animals?.[1]?.name", int)) # None
print(chain.optionalCast("animals?.[1]?.name", str)) # Rabbit
print(chain.optionalGet("animals?.[1]?.ages", int)) # None
print(chain.optionalCast("animals?.[1]?.ages", int)) # 2

print(chain.ensure("animals?.[1]?.type", int)) # 0
print(chain.ensure("animals?.[1]?.ages", int)) # 0
print(chain.ensureCast("animals?.[1]?.ages", int)) # 2

print(chain.ensure("animals?.[1]", JDict)) # {}
print(chain.ensureCast("animals?.[1]", JDict)) # {'name': 'Rabbit', 'type': 'bunny', 'age': 2, 'ages': '2'}

# jlist

animals = chain.ensureCast("animals", JList).chain()
print(animals.ensure("[1]?.name", str)) # Rabbit
print(animals.ensure("[1]?.age", int)) # 0
print(animals.ensureCast("[1]?.age", int)) # 2

print(animals["[1].name"]) # Rabbit
print(animals["[1].age"]) # 2
print(animals["[2].ages"]) # IndexError
print(animals["[2]?.ages"]) # None
