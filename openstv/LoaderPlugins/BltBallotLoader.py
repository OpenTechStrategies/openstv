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

__revision__ = "$Id: BltBallotLoader.py 719 2010-03-01 03:43:54Z jeff.oneill $"

import re
from openstv.plugins import LoaderPlugin

class BltBallotLoader(LoaderPlugin):
  "Ballot loader class for ballots defined by ERS."

  status = 1
  extensions = ["blt"]
  formatName = "ERS"
  
  blankLineRE = re.compile(r'^\s*(?:#.*)?$')
  nCandnSeatsRE = re.compile(r'^\s*(\d+)\s+(\d+)\s*(?:#.*)?$')
  withdrawnRE = re.compile(r'^\s*(-\d+(?:\s+-\d+)*)\s*(?:#.*)?$')
  ballotRE = re.compile(r'^\s*(\d+(?:\s+[\d\-=]+)*)\s+0\s*(?:#.*)?$')
  ballotAndIDRE = re.compile(r'^\s*\(([^\)]+)\)\s+(\d+(?:\s+[\d\-=]+)*)\s+0\s*(?:#.*)?$')
  endOfBallotsRE = re.compile(r'\s*0\s*(?:#.*)?')
  stringRE = re.compile(r'^\s*"([^"]+)"\s*(?:#.*)?$')

  def __init__(self):
    LoaderPlugin.__init__(self)

  def loadFromObject(self, ballotList, f):
    "Load ERS ballot data from a file-like object."
    
    if self.hasCustomBallotIDs(f):
      ballotList.customBallotIDs = True
    
    line = self.getNextNonBlankLine(f)
    (numCandidates, numSeats) = self.getNumCandidatesAndSeats(line)
    ballotList.numCandidates = numCandidates
    ballotList.numSeats = numSeats

    line = self.getNextNonBlankLine(f)
    withdrawn = self.getWithdrawnCandidates(line)
    if withdrawn != []:
      ballotList.withdrawn = withdrawn
      line = self.getNextNonBlankLine(f)

    while not self.atEndOfBallots(line):
      
      if ballotList.customBallotIDs:
        (customID, ballot) = self.getBallotWithCustomID(line)
        ballotList.appendBallot(ballot, customID)
      else:
        (weight, ballot) = self.getBallot(line)
        for i in xrange(weight):
          ballotList.appendBallot(ballot)
      line = self.getNextNonBlankLine(f)

    names = []
    for c in range(numCandidates):
      line = self.getNextNonBlankLine(f)
      name = self.getCandidateName(line)
      names.append(name)
    ballotList.names = names
    
    line = self.getNextNonBlankLine(f)
    ballotList.title = self.getTitle(line)
    
  def hasCustomBallotIDs(self, f):
    self.getNextNonBlankLine(f) # candidates and seats
    self.getNextNonBlankLine(f) # maybe withdrawn candidates
    line = self.getNextNonBlankLine(f) # ballot
    f.seek(0)
    if self.ballotAndIDRE.match(line) is None:
      return False
    else:
      return True
    
  def getNumCandidatesAndSeats(self, line):
    out = self.nCandnSeatsRE.match(line)
    if out is None:
      self.reportLoadError("Cannot process this line:\n\t%s" % line)
    numCandidates = int(out.group(1))
    numSeats = int(out.group(2))
    return numCandidates, numSeats

  def getWithdrawnCandidates(self, line):
    withdrawnCandidates = []
    out = self.withdrawnRE.match(line)
    if out is not None:
      x = out.group(1).split()
      for s in x:
        withdrawnCandidates.append(-int(s) - 1)
    return withdrawnCandidates

  def atEndOfBallots(self, line):
    return self.endOfBallotsRE.match(line) is not None

  def getBallot(self, line):
    out = self.ballotRE.match(line)
    if out is None:
      self.reportLoadError("Cannot process this line:\n\t%s" % line)
    rankings = out.group(1).split()
    weight = int(rankings.pop(0))
    ballot = self.processRankings(rankings)
    return (weight, ballot)

  def getBallotWithCustomID(self, line):
    out = self.ballotAndIDRE.match(line)
    if out is None:
      self.reportLoadError("Cannot process this line:\n\t%s" % line)
    customID = out.group(1)
    rankings = out.group(2).split()
    weight = int(rankings.pop(0))
    if weight != 1:
      self.reportLoadError("Cannot process this line:\n\t%s" % line)
    ballot = self.processRankings(rankings)
    return (customID, ballot)
  
  def processRankings(self, rankings):
    ballot = []
    for item in rankings:
      if item == "-":
        ballot.append(-1)
      elif item.find("=") == -1:
        c = item
        ballot.append(int(c) - 1)
      else:
        ballot.append([int(c) - 1 for c in item.split("=")])
    return ballot
  
  def getCandidateName(self, line):
    out = self.stringRE.match(line)
    if out is None:
      self.reportLoadError("Cannot process this line:\n\t%s" % line)
    name = out.group(1)
    return name
  
  def getTitle(self, line):
    out = self.stringRE.match(line)
    if out is None:
      self.reportLoadError("Cannot process this line:\n\t%s" % line)
    title = out.group(1)
    return title
  
  def getNextNonBlankLine(self, f):
    while True:
      line = f.next()
      if self.blankLineRE.match(line) is None: 
        break
    return line

  def stringifyBallot(self, weight, ballot):
    "Convert a ballot to a string in the BLT format."
    
    line = str(weight)
    
    for item in ballot:
      if isinstance(item, list):
        # Handle equal rankings
        ranking = "=".join([str(c+1) for c in item])
        line += " " + ranking
      else:
        # Single ranking
        c = item
        if c == -1:
          # Skipped ranking
          line += " -"
        else:
          # Just one candidate
          line += " " + str(c+1)
          
    line += " 0"
    return line
  
  def save(self, ballotList, fName=None, packed=False):
    "Save ballots in ERS format."
    
    if fName is not None:
      self.fName = self.normalizeFileName(fName)
    f = open(self.fName, "w")

    f.write("%d %d\n" % (ballotList.numCandidates, ballotList.numSeats))
    
    if ballotList.withdrawn != []:
      withdrawnList = [str(-(c+1)) for c in ballotList.withdrawn]
      f.write(" ".join(withdrawnList) + "\n")

    if packed:
      for i in xrange(ballotList.numWeightedBallots):
        weight, ballot = ballotList.getWeightedBallot(i)
        line = self.stringifyBallot(weight, ballot)
        f.write(line + "\n")
    else:
      for i in xrange(ballotList.numBallots):
        ballot = ballotList.getBallot(i)
        line = self.stringifyBallot(1, ballot)
        if ballotList.customBallotIDs:
          ballotID = ballotList.getBallotID(i)
          f.write("(%s) %s\n" % (ballotID, line))
        else:
          f.write(line + "\n")

    f.write("0\n") # Marker for end of ballot section

    for name in ballotList.names:
      f.write('"%s"\n' % name)
    f.write('"%s"\n' % ballotList.title)

    f.close()
