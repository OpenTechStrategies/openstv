"Plugin module for IRV"

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

__revision__ = "$Id: IRV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import NoSurplusSTV
from openstv.plugins import MethodPlugin

##################################################################

class IRV(NoSurplusSTV, MethodPlugin):
  "Instant Runoff Voting"

  methodName = "IRV"
  longMethodName = "Instant Runoff Voting"
  status = 1

  htmlBody = """
<p>Instant runoff voting (IRV) is more commonly used to elect one
candidate but can also be used to provide semi-proportional representation.
Ballots are first distributed according to their first choices.  The
candidate with the fewest number of ballots is eliminated and the
ballots are transferred to their next choices.  This process is
repeated until the winners are determined.</p>

<p>Instant runoff voting is used by the following cities:</p>
<ul>
<li> San Francisco, CA: http://www.sfgov.org/site/election_index.asp?id=27564
<li> Burlington, VT: http://www.leg.state.vt.us/statutes/fullsection.cfm?Title=24APPENDIX&Chapter=003&Section=00005
<li> Takoma Park, MD: http://www.fairvote.org/media/irv/states/takoma-park-charter-amend.pdf
</ul>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    NoSurplusSTV.__init__(self, b)
    MethodPlugin.__init__(self)

    self.batchElimination = "Zero"
