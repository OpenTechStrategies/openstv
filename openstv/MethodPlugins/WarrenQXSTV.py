"Plugin module for Warren Quasi-Exact STV"

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

__revision__ = "$Id: WarrenQXSTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.qx import RecursiveQXSTV
from openstv.MethodPlugins.WarrenSTV import WarrenSTV
from openstv.plugins import MethodPlugin

##################################################################

class WarrenQXSTV(RecursiveQXSTV, WarrenSTV, MethodPlugin):
  "Warren STV with guard bits and quasi-exact rounding"

  methodName = "WarrenQX STV"
  longMethodName = "WarrenQX STV"
  status = 2
  
  htmlBody = """
<p>Jonathan Lundell's "quasi-exact" implementation of Warren STV.
See David Hill and Jonathan Lundell's paper 
<i>Notes on the Droop quota</i>, available at
http://www.votingmatters.org.uk/ISSUE24/I24P2.pdf,
for a brief description of quasi-exact arithmetic.</p>
"""
  
  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd
  
  def __init__(self, b):
    RecursiveQXSTV.__init__(self, b)
    MethodPlugin.__init__(self)

    self.createGuiOptions(["prec"])
