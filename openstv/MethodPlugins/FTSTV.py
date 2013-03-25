"Plugin module for FTSTV"

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

__revision__ = "$Id: FTSTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

import string

from openstv.STV import WeightedInclusiveSTV
from openstv.plugins import MethodPlugin

##################################################################

class FTSTV(WeightedInclusiveSTV, MethodPlugin):
  "Customizable Fractional Transfer STV"

  methodName = "FTSTV"
  longMethodName = "Fractional Transfer STV"
  status = 2

  htmlBody = """
<p>Fractional transfer STV (FTSTV) is similar to the rules used in
Scotland and is sometimes referred to as the wieighted-inclusive
Gregory method (WIGM).  This implementation contains several options
that allow the user to customize the rules as desired:</p>

<ul>

<li> Precision: The number of digits after the decimal point used
in computing vote values.  Note that FTSTV is implemented using
fixed-point arithmetic.

<li> Threshold: The threshold has three parameters.  First, whether to
use a Droop or a Hare threshold.  Nearly all STV rules use a Droop
threshold.  Second, whether the threshold should decrease as votes are
exhausted.  Third, whether the threshold should be an integer or a
fraction.  For a large number of votes, an integer threshold can
simplify the count, but for a small number of votes, a fractional
threshold is needed to obtain proportionality.

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
             htmlBody + \
             MethodPlugin.htmlEnd

  def __init__(self, b):
    WeightedInclusiveSTV.__init__(self, b)
    MethodPlugin.__init__(self)

    self.prec = 6
    self.threshName = ["Droop", "Static", "Whole"]
    self.delayedTransfer = "Off"
    self.batchElimination = "Zero"
    self.batchCutoff = 0
    self.createGuiOptions(["prec", "thresh0", "thresh1", "thresh2",
                          "delayedTransfer", "batchElimination",
                          "batchCutoff"])

  def preCount(self):
    WeightedInclusiveSTV.preCount(self)

    self.optionsMsg = "Using a %s threshold." % \
                      string.join(self.threshName, "-")
    
