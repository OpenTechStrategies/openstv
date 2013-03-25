"Plugin module for RTSTV"

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

__revision__ = "$Id: RTSTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

import string

from openstv.STV import OrderDependentSTV
from openstv.plugins import MethodPlugin

##################################################################

class RTSTV(OrderDependentSTV, MethodPlugin):
  "Customizable Random Transfer STV"
  
  methodName = "RTSTV"
  longMethodName = "Random Transfer STV"
  status = 2

  htmlBody = """
<p>Random transfer STV (RTSTV) is a method that treats each vote as a
single unit that votes cannot be split up among multiple candidates.
Because the order of the votes can change the outcome of the election,
it is called a "random" transfer method.  This implementation contains
several options that allow the user to customize the rules as desired:</p>

<ul>

<li> Threshold: The threshold has two parameters.  First, whether to
use a Droop or a Hare threshold.  Nearly all STV rules use a Droop
threshold.  Second, whether the threshold should decrease as votes are
exhausted.

<li> Delay Surplus Transfer: Transferring surplus votes is a more
complicated operation than transferring votes from eliminated
candidates.  Some rules delay the transfer of surplus votes where
candidates can be safely eliminated (i.e., the candidates are sure to
lose regardless of which candidates receive the surplus votes).

<li> Candidate Elimination: This option applies to the elimination of candidates.
"None" means that candidates are always eliminated one by one.
"Zero" means that all candidates with zero votes are eliminated simultaneously.
"Losers" means that all losing candidates are eliminated simultaneously.
"Batch" means that at the first elimination round all candidates under a
specified threshold are eliminated.

<li> Batch Cutoff: This is the threshold to apply when Candidate Elimination is
set to "Batch".

</ul>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    OrderDependentSTV.__init__(self, b)
    MethodPlugin.__init__(self)

    self.threshName = ["Droop", "Static", "Whole"]
    self.delayedTransfer = "Off"
    self.batchElimination = "Zero"
    self.batchCutoff = 50
    self.createGuiOptions(["thresh0", "thresh1", "delayedTransfer",
                          "batchElimination", "batchCutoff"])

  def preCount(self):
    OrderDependentSTV.preCount(self)

    self.optionsMsg = "Using a %s threshold." % \
                      string.join(self.threshName, "-")
    
  def transferSurplusVotesFromCandidate(self, cSurplus):
    "Transfer surplus votes with random transfer rules."

    # transfer whole votes in excess of the threshold
    surplus = int(self.count[self.R-1][cSurplus] - self.thresh[self.R-1])
    for i in self.votes[cSurplus][:surplus]:
      c = self.b.getTopChoiceFromBallot(i, self.continuing)
      self.votes[cSurplus].remove(i)
      if c != None:
        self.votes[c].append(i)

    desc = "Count after transferring surplus votes from %s. " \
         % self.b.names[cSurplus]
    return desc

  def transferVotesFromCandidates(self, elimList):
    "Eliminate candidates according to the random transfer rules."

    # Transfer whole votes from losers.
    for loser in elimList:
      for i in self.votes[loser]:
        c = self.b.getTopChoiceFromBallot(i, self.continuing)
        if c != None:
          self.votes[c].append(i)
      self.votes[loser] = []

    elimList.sort()
    desc = "Count after eliminating %s and transferring votes. " \
          % self.b.joinList(elimList)
    return desc
