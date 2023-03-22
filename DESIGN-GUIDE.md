> # **Note**
>
> **This guide may be subject to change!**

# Introduction

This guide serves as a reference point to be able to design code consistently in the project.


# Basics

The [PEP8] needs be respected and serves as a foundation.

Furthermore, the [NumPy-style][] is used for docstrings.


# Code Structure

The code should follow following structure:
  1. [`__all__`](#1)
  2. [`import`s](#2)
  3. [logger and constants](#3)
  4. [code](#4)

## 1
A tuple defining what should be public accessible (at least via wildcard).

Examples:
~~~py
__all__ = ()  # nothing should be public
__all__ = ("Foo",)  # only Foo should be public
__all__ = ("Foo", "Bar", "egg", "spam")  # Foo, Bar, egg and spam are public
~~~

## 2
Imports should always be specific and point directly towards the source (e.g. `from Alberto3.utils import get_logger` instead of `from AlbertoX3 import get_logger`).

For the structure see [#Import Structure](#import-structure).

## 3
The logger should be the defined before any constant.

The logger should be initialized like this:
~~~py
from Alberto3.utils import get_logger
logger = get_logger()
~~~

Full example of constants and logger:
~~~py
from Alberto3.utils import get_logger

logger = get_logger()
FOO: set[str] = {"bar", "egg"}
SPAM: bool = True
~~~

> Note: the logger will automatically detect the name to use. *It defaults to the folder-path inside the extensions-folder.*

## 4
Nothing spezial (by now), just follow [PEP8][].


# Import Structure
All imports should be ordered alphabetically (from `A` to `Z` and then from `a` to `z`).

Also, they should follow following structure:
1. `import Foo`
2. `from foo import bar`/`from foo.bar import egg`
3. `from API import foo`/`from API.foo import bar`</br>
   (`API` referring to `interactions` in this case)
4. `from AlbertoX3.foo import bar`
5. `from .foo import bar`

A practical example:
~~~py
# see 1
import re
import sys

# see 2
from asyncio.locks import Event
from io import StringIO
from pathlib import Path

# see 3
from interactions.models.discord.guild import Guild
from interactions.models.discord.user import Member, User

# see 4
from AlbertoX3.constants import Config
from AlbertoX3.utils import get_logger

# see 5
from .colors import Color
~~~
> Note: import-groups (1-5) should be separated by an empty line


<!--- References --->
[PEP8]: https://www.python.org/dev/peps/pep-0008/
[NumPy-style]: https://numpydoc.readthedocs.io/en/latest/format.html
