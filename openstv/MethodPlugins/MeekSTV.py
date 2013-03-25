"Plugin module for Meek STV"

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

__revision__ = "$Id: MeekSTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import RecursiveSTV
from openstv.plugins import MethodPlugin

##################################################################

class MeekSTV(RecursiveSTV, MethodPlugin):
  "Meek STV"

  methodName = "Meek STV"
  longMethodName = "Meek STV"
  status = 1

  htmlBody = """
<p>Meek STV provide more accurate proportional representation than
other STV methods, but the count must be done with a computer and
cannot be done by hand.  There are two main differences between Meek
STV and other STV methods: (1) winning candidates still receive vote
transfers and (2) when a candidate is eliminated, the votes are
transferred as if the candidate never entered the election.</p>
"""
  
  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    RecursiveSTV.__init__(self, b)
    MethodPlugin.__init__(self)
    self.createGuiOptions(["prec", "thresh0", "thresh1", "thresh2"])
    
  def updateCount(self, tree=None, remainder=None):
    "Traverse the tree to count the ballots."
    
    if tree is None: 
      tree = self.tree
    if remainder is None: 
      remainder = self.p
    
    # Iterate over the next candidates on the ballots
    count = self.count[self.R]
    keepFactor = self.keepFactor[self.R]
    p = self.p
    updateCount = self.updateCount
    for c in tree:
      if c == "n" or c == "bi": 
        continue
      rrr = remainder
      count[c] += rrr * keepFactor[c] * tree[c]["n"] / p
      rrr = rrr * (self.p - keepFactor[c]) / p
      # If ballot not used up, keep going
      if rrr > 0:
        updateCount(tree[c], rrr)
