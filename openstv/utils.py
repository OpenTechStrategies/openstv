"Module of generally useful utilities."

## OpenSTV Copyright (C) 2003-2010 Jeffrey O'Neill
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

__revision__ = "$Id: OpenSTV.py 508 2009-04-29 00:51:56Z jco8 $"

import os.path
import sys

def getHome():
  if hasattr(sys, "frozen"):
    if sys.platform == "darwin": # OS X
      return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), "Resources")
    return os.path.dirname(sys.executable)
  else:
    return os.path.dirname(__file__)

def pluralize(count, singular="", plural="s"):
  "return singular version if count is 1; else return plural version"
  if count == 1:
    return singular
  return plural

