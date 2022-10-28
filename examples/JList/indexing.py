# You worry about IndexOutOfRange exceptions

from pyaddict import JList

gallery = [ "image.png", "otherImage.png" ]
gallery2 = [ ] # empty gallery :/

jlist = JList(gallery)
jlist2 = JList(gallery2)

# with normal lists
wallpaper = gallery[0] # "image.png"
print(wallpaper) # "image.png"
try:
    wallpaper = gallery2[0] # IndexError: list index out of range
except IndexError as e:
    print(e)

# JList can handle this
wallpaper = jlist.ensure(0, str) # "image.png"
print(wallpaper) # "image.png"
wallpaper = jlist2.ensure(0, str) # ""
print(wallpaper) # ""
