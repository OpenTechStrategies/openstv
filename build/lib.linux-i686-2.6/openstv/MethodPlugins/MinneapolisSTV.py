"Plugin module for Minneapolis STV"

## Copyright 2009-2010 Jeffrey O'Neill
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

__revision__ = "$Id: MinneapolisSTV.py 718 2010-02-28 21:02:44Z jlundell $"

from openstv.STV import WeightedInclusiveSTV
from openstv.plugins import MethodPlugin

##################################################################

class MinneapolisSTV(WeightedInclusiveSTV, MethodPlugin):
  "Minneapolis STV"

  methodName = "Minneapolis STV"
  longMethodName = "Minneapolis STV"
  status = 0

  htmlBody = """
<p>Minneapolis enacted these rules for certain local elections in 2009.
The current ordinance, as amended 2009-10, is available here: 
http://www.ci.minneapolis.mn.us/council/2009-meetings/20091002/docs/Ordinance-Ch167.pdf.
This implementation has not been verified.</p>
<p>The referenced ordinance has an internal conflict:</p>
<blockquote>
Mathematically impossible to be elected means either: 
(1) the candidate could never win because his or her current vote
total plus all votes that could possibly be transferred to him or her in future rounds 
(from candidates with fewer votes, tied candidates, and surplus votes) 
would not be enough to surpass the candidate with the next higher current vote total; or
(2) the candidate has a lower current vote total than a candidate who is described by (1).
</blockquote>
<p>Contrary to the text, mathematical impossibility requires the phrase "enough to surpass"
to read instead "enough to tie or surpass". This implementation implements the latter
condition, consistent with mathematical impossibility.</p>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    WeightedInclusiveSTV.__init__(self, b)
    MethodPlugin.__init__(self)
    
    self.prec = 4
    self.threshName = ["Droop", "Static", "Whole"]
    self.delayedTransfer = "On"
    self.batchElimination = "Losers"
    self.weakTieBreakMethod = "strong"

  def transferSurplusVotesFromCandidate(self, cSurplus):
    "Transfer the surplus votes of one candidate."

    # Transfer all of the votes at a fraction of their value
    surplus = self.count[self.R-1][cSurplus] - self.thresh[self.R-1]
    # Calculate surplus fraction to specified precision
    surplusFraction = (surplus * self.p)/self.count[self.R-1][cSurplus]
    for i in self.votes[cSurplus][:]:
      self.transferValue[i] = self.transferValue[i] * surplusFraction / self.p
      c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
      if c is not None:
        self.votes[c].append(i)

    self.votes[cSurplus] = []
    
    desc = "Count after transferring surplus votes from %s with a transfer "\
         "value of %s/%s. " % \
         (self.b.names[cSurplus], 
          self.displayValue(surplus),
          self.displayValue(self.count[self.R-1][cSurplus]))
    return desc
