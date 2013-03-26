"Plugin module for GPCA2000STV"

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

__revision__ = "$Id: GPCA2000STV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import WeightedInclusiveSTV
from openstv.plugins import MethodPlugin

##################################################################

class GPCA2000STV(WeightedInclusiveSTV, MethodPlugin):
  "Green Party of California STV"

  methodName = "GPCA2000 STV"
  longMethodName = "Green Party of California STV"
  status = 2

  htmlBody = """
<p>The Green Party of California (GPCA) adopted these rules in 2000.
The rules are described in the GPCA bylaws, available at
http://cagreens.org/bylaws/.  The rules are based on the
description of STV found in <i>Electoral System Design: The New
International IDEA Handbook</i>
(http://www.idea.int/publications/esd/index.cfm), except that
GPCA uses a fractional threshold, and does not elect candidates that
do not reach the a full (static) threshold.</p>

<p>Neither IDEA nor the GPCA bylaws specify a method of breaking ties.
This implementation breaks all ties randomly. See Jonathan Lundell's
paper <i>Random tie-breaking in STV</i>, available at
http://www.votingmatters.org.uk/ISSUE22/I22P1.pdf,
for the rationale.</p>
"""
  
  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    WeightedInclusiveSTV.__init__(self, b)
    MethodPlugin.__init__(self)
    
    self.prec = 5
    self.weakTieBreakMethod = "strong"	# treat all ties as strong
    self.threshName = ["Droop", "Static", "Fractional"]
    self.delayedTransfer = "Off"
    self.batchElimination = "Zero"
    # Election is over when we have enough winners or all candidates
    # have been eliminated.
    self.stopCond = ["Know Winners", "Continuing Empty"]

  def updateCandidateStatus(self):
    "Update candidate status at end of election."

    self.newLosers(list(self.continuing))
