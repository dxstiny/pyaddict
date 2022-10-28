# Your list contains different types

from pyaddict import JList

array = [ 1, 2.0, "Hello", True, [ 1, 2, 3 ], { "a": 1, "b": 2 } ] # I hope you never have to use such a list
jlist = JList(array)

# with normal lists you would have to do this
print(array[0]) # 1
print(array[1]) # 2.0
print(array[2]) # "Hello"
print(array[3]) # True
print(array[4]) # [ 1, 2, 3 ]
print(array[5]) # { "a": 1, "b": 2 }
# easy until now
print(array[0] + array[1]) # 3.0
try:
    print(array[1] + array[2]) # TypeError: unsupported operand type(s) for +: 'float' and 'str'
except TypeError as e:
    print(e)
try:
    print(array[2] + array[3]) # TypeError: can only concatenate str (not "bool") to str
except TypeError as e:
    print(e)
try:
    print(array[4] + array[5]) # TypeError: can only concatenate list (not "dict") to list
except TypeError as e:
    print(e)
# but this is probably not what you want

# JList can handle this
print(jlist.ensureCast(0, int)) # 1
print(jlist.ensureCast(1, float)) # 2.0
print(jlist.ensureCast(2, str)) # "Hello"
print(jlist.ensureCast(3, bool)) # True
print(jlist.ensureCast(4, list)) # [ 1, 2, 3 ]
print(jlist.ensureCast(5, dict)) # { "a": 1, "b": 2 }
# just like normal lists, but with type safety
print(jlist.ensureCast(0, int) + jlist.ensureCast(1, int)) # 3.0
print(jlist.ensureCast(1, str) + jlist.ensureCast(2, str)) # "2.0Hello"
print(jlist.ensureCast(2, str) + jlist.ensureCast(3, str)) # "HelloTrue"
print(jlist.ensureCast(4, list) + jlist.ensureCast(5, list)) # [ 1, 2, 3, "a", "b" } ]
