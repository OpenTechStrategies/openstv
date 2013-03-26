"Plugin module for Bucklin"

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

__revision__ = "$Id: Bucklin.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import Iterative
from openstv.plugins import MethodPlugin

##################################################################

class Bucklin(Iterative, MethodPlugin):
  "Bucklin system"

  methodName = "Bucklin"
  longMethodName = "Bucklin System"
  onlySingleWinner = True
  threshMethod = False
  status = 2

  htmlBody = """
<p>The Bucklin system is also known as the Grand Junction system
(where it was once used) and American preferential voting.  The
Bucklin system has been used for electing a single candidate and also
for electing multiple candidates, but this implementation can only be
used to elect one candidate.</p>

<p>In electing a single candidate, a candidate receiving a majority of
first choices is declared the winner.  If no candidate has a majority
of first choices, then a candidate receiving a majority of first and
second choices is the winner.  If more than one candidate has a
majority of first and second choices, then the candidate having the
most first and second choices is the winner.  This process is repeated
for further choices as necessary.</p>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    Iterative.__init__(self, b)
    MethodPlugin.__init__(self)
    self.prec = 0

  def countBallots(self):
    "Count the votes with the Bucklin system."

    # Sequentially use more candidates until we have a winner.
    for self.R in range(self.b.numCandidates):

      self.allocateRound()
      self.roundInfo[self.R]["action"] = ("", [])

      if self.R == 0:
        self.msg[self.R] += "Count of first choices. "
      else:
        self.msg[self.R] += "No candidate has a majority. "\
                            "Using %d rankings. " % (self.R+1)
        self.count[self.R] = self.count[self.R-1][:]
        self.exhausted[self.R] = self.exhausted[self.R-1]

      # Count votes using multiple rankings
      for i in xrange(self.b.numWeightedBallots):
        weight, blt = self.b.getWeightedBallot(i)
        if len(blt) > self.R:
          c = blt[self.R]
          self.count[self.R][c] += weight
        else:
          self.exhausted[self.R] += weight

      # Check for winners.  Could be more than we need.
      potWinners = []
      for c in self.continuing:
        if 2*self.count[self.R][c] > self.b.numBallots:
          potWinners.append(c)
      if len(potWinners) > 0:
        (c, desc) = self.breakWeakTie(self.R, potWinners, "most", "winner")
        desc += self.newWinners([c])
        self.msg[self.R] += desc
        break

    # If no candidate has a majority then a plurality is good enough
    if len(self.winners) == 0:
      (c, desc) = self.breakWeakTie(self.R, self.continuing, "most", "winner")
      desc += self.newWinners([c], "under")
      self.msg[self.R] += desc
