"Plugin module for SNTV"

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

__revision__ = "$Id: SNTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import NonIterative
from openstv.plugins import MethodPlugin

##################################################################

class SNTV(NonIterative, MethodPlugin):
  "Single Non-Transferable Vote"

  methodName = "SNTV"
  longMethodName = "Single Non-Transferable Vote"
  status = 1
    
  htmlBody = """
<p>With the single non-transferable vote, only the first choices are
used in counting the ballots, and the candidate with the greatest
number of first choices is the winner.  When there is only one seat to
be filled, this corresponds to a traditional plurality election.  When
there is more than one seat to be filled, this provides a simple form
of proportional representation.</p>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd
  
  def __init__(self, b):
    NonIterative.__init__(self, b)
    MethodPlugin.__init__(self)
    
  def countBallots(self):
    "Count the votes using SNTV."

    # Count the first place votes
    candidates = set(range(self.b.numCandidates))
    for i in xrange(self.b.numWeightedBallots):
      c = self.b.getTopChoiceFromWeightedBallot(i, candidates)
      if c == None:
        self.exhausted += self.b.getWeight(i)
      else:
        self.count[c] += self.b.getWeight(i)
    self.msg += ("Count of first choices. ")

    # Choose the winners
    desc = self.chooseWinners()
    self.msg += desc
