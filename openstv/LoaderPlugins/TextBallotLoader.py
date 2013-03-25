"Plugin module for simple text format ballots."

## Copyright (C) 2003-2010  Jeffrey O'Neill
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

__revision__ = "$Id: TextBallotLoader.py 719 2010-03-01 03:43:54Z jeff.oneill $"

import re
from openstv.plugins import LoaderPlugin

class TextBallotLoader(LoaderPlugin):
  "Class for ballots with a simple text format."

  status = 1
  extensions = ["txt", "text"]
  formatName = "Text"
  
  commentRE = re.compile("#.*")

  def __init__(self):
    LoaderPlugin.__init__(self)

  def loadFromObject(self, ballotList, f):
    "Load text ballot data from a file-like object"

    # Load ballots in two passes.  On the first pass, get all the candidate
    # names, and on the second pass, add the ballots.  The ballots class
    # needs to know how many candidates there are before we add any ballots.

    # First pass
    allNames = set()
    for line in f.readlines():
      
      line = self.commentRE.sub("", line) # strip comment
      
      # get optional weight
      y = re.match("\s*(\d+)\s*:", line)
      if y is None:
        weight = 1
      else:
        weight = int(y.group(1))
        line = line[y.end():]

      ballotNames = self.getBallot(line)
      for name in ballotNames:
        allNames.add(name)

    ballotList.names = allNames

    # Second pass
    f.seek(0)
    for line in f.readlines():

      line = self.commentRE.sub("", line) # strip comment
      
      # get optional weight
      y = re.match("\s*(\d+)\s*:", line)
      if y is None:
        weight = 1
      else:
        weight = int(y.group(1))
        line = line[y.end():]

      names = self.getBallot(line)
      for i in xrange(weight):
        ballotList.appendBallotUsingNames(names)
        
  def getBallot(self, line):
    line = line.strip()
    if line == "":
      return []
    z = re.match("[\w\s]*$", line)
    if z is None:
      self.reportLoadError("Cannot process this line:\n\t%s" % line)
    else:
      names = line.split()
    return names

  def save(self, ballotList, fName=None, packed=False):
    "Save text ballots to a file."
    
    if fName is not None:
      self.fName = self.normalizeFileName(fName)
    f = open(self.fName, "w")

    if not ballotList.isalnum():
      raise RuntimeError, """\
Can't save ballots in text format.  The
candidates' names must be alphanumeric with
no white space."""

    if packed:
      for i in xrange(ballotList.numWeightedBallots):
        weight, ballot = ballotList.getWeightedBallot(i)
        b = [ballotList.names[c] for c in ballot]
        f.write("%d: %s\n" % (weight, ' '.join(b)))
    else:
      for i in xrange(ballotList.numBallots):
        ballot = ballotList.getBallot(i)
        b = [ballotList.names[c] for c in ballot]
        f.write("%s\n" % (' '.join(b)))

    f.close()
