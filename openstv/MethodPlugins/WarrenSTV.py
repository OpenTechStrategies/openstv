"Plugin module for Warren STV"

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

__revision__ = "$Id: WarrenSTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import RecursiveSTV
from openstv.plugins import MethodPlugin

##################################################################

class WarrenSTV(RecursiveSTV, MethodPlugin):
  "Warren STV"

  methodName = "Warren STV"
  longMethodName = "Warren STV"
  status = 2

  htmlBody = """
<p>Warren STV is similar to Meek STV except that surplus votes are transferred
in a different way.</p>
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
    for c in tree.keys():
      if c == "n" or c == "bi": 
        continue
      rrr = remainder
      if self.keepFactor[self.R][c] < rrr:
        self.count[self.R][c] += self.keepFactor[self.R][c] * tree[c]["n"]
        rrr -= self.keepFactor[self.R][c]
      else:
        self.count[self.R][c] += rrr * tree[c]["n"]
        rrr = 0
      # If ballot not used up and more candidates, keep going
      if rrr > 0:
        self.updateCount(tree[c], rrr)
