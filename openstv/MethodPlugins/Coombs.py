"Plugin module for Coombs"

## Copyright (C) 2003-2010 Jeffrey O'Neill
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

__revision__ = "$Id: Coombs.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import NoSurplusSTV
from openstv.plugins import MethodPlugin

##################################################################

class Coombs(NoSurplusSTV, MethodPlugin):
  "Coombs"
  
  methodName = "Coombs"
  longMethodName = "Coombs Method"
  status = 2

  htmlBody = """
<p>Coombs is the same as instant runoff except that the candidate receiving the
most last-place votes (instead of the fewest first-place votes) is
eliminated at each round.  If a ballot does not rank all of the
candidates, then the unranked candidates share the last-place vote.</p>
"""
  
  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    NoSurplusSTV.__init__(self, b)
    MethodPlugin.__init__(self)

    self.stopCond = ["N"]
    self.batchElimination = "None"
    self.unranked = []

  def preCount(self):
    NoSurplusSTV.preCount(self)
    
    # Create data structures for speeding up mostLast()
    self.unranked = [None] * self.b.numWeightedBallots
    for i in xrange(self.b.numWeightedBallots):
      u = []
      b = self.b.getWeightedBallot(i)[1]
      for c in self.continuing:
        if c in b: 
          continue
        u.append(c)
      self.unranked[i] = u
    
  def mostLast(self):
    "Count the number of last-place votes per candidate."

    desc = ""

    # Count last place votes per candidate
    total = [0] * self.b.numCandidates
    for i in xrange(self.b.numWeightedBallots):
      nUnranked = len(self.unranked[i])
      weight, blt = self.b.getWeightedBallot(i)
      # If no unranked cands, last place candidate gets the vote
      if nUnranked == 0:
        ballot = blt[:]
        ballot.reverse()
        for c in ballot:
          if c in self.continuing:
            break
        total[c] += weight
      # Otherwise unranked cands share the last place vote
      else:
        share = 1.0 * weight / nUnranked
        for c in self.unranked[i]:
          total[c] += share

    # Resolve ties
    ctng = list(self.continuing)
    ctng.sort(key=lambda a, f=total: -f[a])
    c0 = ctng[0]
    numTied = total.count(total[c0])
    if numTied > 1:
      desc += "Candidates %s were tied when choosing a candidate to "\
              "eliminate. " % self.b.joinList(ctng[:numTied])
      (c0, desc2) = self.breakStrongTie(ctng[:numTied])
      desc += desc2

    desc += "Last place votes: "
    ctng.sort()
    for c in ctng[:-1]:
      desc += "%s, %f; "  % (self.b.names[c], total[c])
    c = ctng[-1] 
    desc += "and %s, %f. "  % (self.b.names[c], total[c])

    # Update data structures
    for i in xrange(self.b.numWeightedBallots):
      if c0 in self.unranked[i]: 
        self.unranked[i].remove(c0)

    return (c0, desc)

  def selectCandidatesToEliminate(self):
    "Choose candidates to eliminate."

    (c, desc) = self.mostLast()
    self.newLosers([c])
    elimList = [c]
    return (elimList, desc)
