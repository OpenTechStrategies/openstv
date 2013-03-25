"Plugin module for Approval voting"

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

__revision__ = "$Id: Approval.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import NonIterative
from openstv.plugins import MethodPlugin

##################################################################

class Approval(NonIterative, MethodPlugin):
  "Implement approval voting"

  methodName = "Approval"
  longMethodName = "Approval Voting"
  status = 1

  htmlBody = """
<p>With approval voting, a voter can approve of as many candidates as
he or she likes, and the candidate approved of by the greatest number
of voters is elected.  A voter approves of a candidate by listing the
candidate on the ballot, and the order of the candidates on the ballot
makes no difference.</p>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    NonIterative.__init__(self, b)
    MethodPlugin.__init__(self)

  def countBallots(self):
    "Count the votes using approval voting."

    # Count the approvals
    for i in xrange(self.b.numWeightedBallots):
      weight, blt = self.b.getWeightedBallot(i)
      for j in blt:
        self.count[j] += weight

    self.msg += "Count of all approvals. "

    # Choose the winners
    desc = self.chooseWinners()
    self.msg += desc
