# You're dealing with nested objects

from typing import Optional
from pyaddict import JDict

match = {
    "home": {
        "name": "Liverpool",
        "score": 2
    },
    "away": {
        "name": "Chelsea",
        "score": 1
    }
}

match2 = {
    "home": {
        "name": "Manchester City",
        "score": 3
    },
    # opponent is not known yet
}

jdict = JDict(match)
jdict2 = JDict(match2)

# with normal dicts
print(match["home"]) # { "name": "Liverpool", "score": 2 }
print(match["away"]) # { "name": "Chelsea", "score": 1 }
print(match2["home"]) # { "name": "Manchester City", "score": 3 }
try:
    print(match2["away"]) # KeyError: 'away'
except KeyError as e:
    print(e)

# JDict can handle this
print(jdict.ensure("home", dict)) # { "name": "Liverpool", "score": 2 }
print(jdict.ensure("away", dict)) # { "name": "Chelsea", "score": 1 }
print(jdict2.ensure("home", dict)) # { "name": "Manchester City", "score": 3 }
print(jdict2.ensure("away", dict)) # { }

# if you're now to access the name of the team, you would have to do this
print(match["home"]["name"]) # "Liverpool"
print(match["away"]["name"]) # "Chelsea"
print(match2["home"]["name"]) # "Manchester City"
try:
    print(match2["away"]["name"]) # KeyError: 'away'
except KeyError as e:
    # here you can't even access the name of the team
    print(e)
# you could fix the key error:
print(match2.get("away", dict()).get("name", str())) # ""

# JDict can handle this
print(jdict2.ensureCast("away", JDict).ensure("name", str)) # ""

# so is it just more verbose?
# no, because jdict offers more features
print(type(match2.get("home", dict()).get("name"))) # Any | None -> <class 'str'>
print(type(match2.get("away", dict()).get("name"))) # Any | None -> <class 'NoneType'>
print(type(match2.get("away", dict()).get("name", None))) # Any | None -> <class 'NoneType'>
# you can't specify the type you want; you can only specify the default value
# if you want to specify the type, you have to do this
name: Optional[str] = match2.get("away", dict()).get("name")
# but this is not safe, because you can't be sure that the value is a string:
score: Optional[str] = match2.get("home", dict()).get("score")
print(type(score), score) # <class 'int'> 3

# JDict offers this out of the box
print(type(jdict2.ensureCast("home", JDict).optionalGet("name", str))) # str | None -> <class 'str'>
print(type(jdict2.ensureCast("away", JDict).optionalGet("name", str))) # str | None -> <class 'NoneType'>
# your IDE knows the type of the value already
name = jdict2.ensureCast("away", JDict).optionalGet("name", str)
score = jdict2.ensureCast("home", JDict).optionalGet("score", str)
print(type(score), score) # <class 'NoneType'> None
score = jdict2.ensureCast("home", JDict).optionalGet("score", int)
print(type(score), score) # <class 'int'> 3
