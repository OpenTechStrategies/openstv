"Plugin module for Borda"

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

__revision__ = "$Id: Borda.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import NonIterative
from openstv.plugins import MethodPlugin

##################################################################

class Borda(NonIterative, MethodPlugin):
  "Borda count"

  methodName = "Borda"
  longMethodName = "Borda Count"
  status = 1

  htmlBody = """
<p>With the Borda count, candidates recieve points based on their
position on the ballots.  For example, if there are 4 candidates, then
a candidate receives 3 points for every first choice, 2 points for
every second choice, and 1 point for every third choice.  A candidate
receives no points if ranked last or not ranked at all.  Borda
provides some proportionality but not as well as SNTV, IRV, or
STV.</p>

<p>As an option, the ballots can by "completed" whereby unranked
candidates share the remaining points on a ballot.  This option
prevents one type of strategic voting whereby a voter ranks only
his or her first choice candidate.</p> 
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    NonIterative.__init__(self, b)
    MethodPlugin.__init__(self)

    self.ballotCompletion = "Off"
    self.createGuiOptions(["ballotCompletion"])
    
  def preCount(self):
    NonIterative.preCount(self)

    assert(self.ballotCompletion in ["On", "Off"])
    
    if self.ballotCompletion == "On":
      # The only fractions that will ever appear because of ballot completion
      # is 1/2 so no more precision is necessary.
      self.optionsMsg = "Using ballot completion."
      self.prec = 1
    else:
      self.optionsMsg = "Not using ballot completion."
      self.prec = 0
    self.p = 10**self.prec

  def countBallots(self):
    "Count the votes using the Borda Count."

    # Add up the Borda counts
    for i in xrange(self.b.numWeightedBallots):
      weight, blt = self.b.getWeightedBallot(i)
      # Ranked candidates get their usual Borda score
      for j, c in enumerate(blt):
        self.count[c] += self.p * weight * (self.b.numCandidates-j-1)

      # If doing ballot completion, then unranked candidates share the
      # remaining Borda score.  Otherwise, goes to exhausted pile.
      if len(blt) < self.b.numCandidates-1:
        nMissingCand = self.b.numCandidates - len(blt)
        # missingCandCount = nMissingCand*(nMissingCand-1)/2/nMissingCand
        # simplifies to  missingCandCount = (nMissingCand-1)/2
        if self.ballotCompletion == "On":
          for c in range(self.b.numCandidates):
            if c not in blt:
              self.count[c] += self.p * weight * \
                                  (nMissingCand-1) / 2
        else:
          self.exhausted += self.p * weight * \
                            (nMissingCand-1) * nMissingCand / 2

    self.msg += "Borda count totals. "

    # Choose the winners
    desc = self.chooseWinners()
    self.msg += desc
