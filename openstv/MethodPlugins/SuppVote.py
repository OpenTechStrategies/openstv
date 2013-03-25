"Plugin module for the Supplemental Vote"

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

__revision__ = "$Id: SuppVote.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import NoSurplusSTV
from openstv.plugins import MethodPlugin

##################################################################

class SuppVote(NoSurplusSTV, MethodPlugin):
  "Supplemental Vote"

  methodName = "Supplemental Vote"
  longMethodName = "Supplemental Vote"
  onlySingleWinner = True
  status = 2

  htmlBody = """
<p>The supplemental vote is a simplified version of IRV.  Only the first
two rankings on the ballots are used.  In the first round, the first
rankings are counted and all candidates except for the top two are
eliminated.  Ballots of eliminated candidates are transferred to their
second rankings.  The supplemental vote is used to elect the Mayor of
London.</p>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd
  
  def __init__(self, b):
    NoSurplusSTV.__init__(self, b)
    MethodPlugin.__init__(self)
    
  def selectCandidatesToEliminate(self):
    "Eliminate all candidates except for the top two."

    (topTwo, desc) = self.chooseNfromM(2, self.count[0], self.continuing,
                                       "top two candidates")
    loserList = []
    for c in self.continuing:
      if c not in topTwo:
        loserList.append(c)

    self.newLosers(loserList)        
    return (loserList, desc)
