"Plugin module for ERS format ballots."

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

## set this first:    ballotList.numCandidates = [numCandidates]

__revision__ = "$Id: DCBallotLoader.py 693 2010-01-03 19:12:05Z jeff.oneill $"

import re
from openstv.plugins import LoaderPlugin

class DCBallotLoader(LoaderPlugin):
  "Ballot loader class for DemoChoice ballot files."

  status = 0
  extensions = ["dc"]
  formatName = "DC"
  
  def __init__(self):
    LoaderPlugin.__init__(self)
    self.maxCandidateNumber = 0

  def loadFromObject(self, ballotList, f):
    """Load DemoChoice ballot data from a file-like object.
    
    For this loader, user must set the number of candidates in the Ballots
    object before loading the ballots since the ballot file does not have
    this information.
    """
    
    assert(ballotList.numCandidates > 0)
    for line in f.readlines():
      ballot = self.getBallot(line)
      ballotList.appendBallot(ballot)
      
  def getBallot(self, line):
    line = line.strip()
    z = re.match("[\d,]*$", line)
    if z is None:
      self.reportLoadError("Cannot process this line:\n\t%s" % line)
    rankings = line.split(',')
    ballot = [int(c) for c in rankings]
    return ballot

  def save(self, ballotList, fName=None):
    "Save ballots in DC format."
    
    if fName is not None:
      self.fName = self.normalizeFileName(fName)
    f = open(self.fName, "w")
    
    for i in xrange(ballotList.numBallots):
      ballot = ballotList.getBallot(i)
      line = ",".join(ballot)
      f.write(line + "\n")

    f.close()
