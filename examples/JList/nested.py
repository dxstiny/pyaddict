# You're dealing with nested lists

from pyaddict import JList

array = [ [ 1, 2, 3 ], [ "4", "5", "6" ], "I'm not even a list" ]
jlist = JList(array)

# with normal lists
print(array[0]) # [ 1, 2, 3 ]
print(array[1]) # [ "4", "5", "6" ]
print(array[2]) # "I'm not even a list"
# easy until now
print(array[0][0]) # 1
print(array[1][0]) # "4"
print(array[2][0]) # I
# but this might not be what you want

# JList can handle this
print(jlist.ensure(0, list)) # [ 1, 2, 3 ]
print(jlist.ensure(1, list)) # [ "4", "5", "6" ]
print(jlist.ensure(2, list)) # [ ]
print(jlist.ensure(2, str)) # "I'm not even a list"
print(jlist.ensureCast(2, list)) # ['I', "'", 'm', ' ', 'n', 'o', 't', ' ', 'e', 'v', 'e', 'n', ' ', 'a', ' ', 'l', 'i', 's', 't']

print(jlist.ensureCast(0, JList).ensure(0, int)) # 1
print(jlist.ensureCast(1, JList).ensure(0, str)) # "4"
print(jlist.ensureCast(1, JList).ensureCast(0, int)) # 4
print(jlist.ensureCast(2, JList).ensure(0, str)) # I
