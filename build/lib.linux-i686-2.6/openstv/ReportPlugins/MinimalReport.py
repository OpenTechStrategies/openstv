"Plugin module for generating a minimal report."

## Copyright (C) 2010 Jeffrey O'Neill
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

from openstv.plugins import ReportPlugin

class MinimalReport(ReportPlugin):
  "Return a minimal text report that is not meant for human consumption."

  status = 0
  reportName = "minimal"
  
  def __init__(self, e, outputFile=None, test=False):
    ReportPlugin.__init__(self, e, outputFile, test)
    
  def generateHeader(self):
    "Header line is a sorted list of winning candidate index numbers."
    winners = list(self.e.winners)
    winners.sort()
    self.output(",".join(str(x) for x in winners) + "\n")
    
  def generateReportNonIterative(self):
    """Minimal report for noniterative methods contains two lines.  The first
    line is a list of winning candidates presented as sorted index numbers.
    The second line has a fake round number (i.e., "1") followed by a list of 
    candidate counts and exhausted votes."""

    self.generateHeader()
    
    line = "1," # Fake round number
    line += ",".join(self.e.displayValue(x) for x in self.e.count)
    line += ",%s" % self.e.displayValue(self.e.exhausted)
    self.output(line + "\n")

  def generateReportIterative(self):
    """Minimal report for iterative methods contains a winners line and one
    line for each round.  The winners line is a list of winning candidates 
    presented as sorted index numbers.  The round lines have a round number 
    followed by a list of candidate counts and exhausted votes."""

    self.generateHeader()
    
    for r in range(self.e.numRounds):
      roundStage = r
      if self.e.methodName == "ERS97 STV":
        roundStage = self.e.roundToStage(r)
      
      line = "%s," % (roundStage + 1) 
      line += ",".join(self.e.displayValue(x) for x in self.e.count[r])
      line += ",%s" % self.e.displayValue(self.e.exhausted[r])
      self.output(line + "\n")

  def generateReportCondorcet(self):
    """Minimal report for Condorcet methods contains a winners line and the
    pairwise comparison matrix."""
    
    self.generateHeader()
    
    for c in range(self.cleanB.numCandidates):
      self.output(",".join(str(x) for x in self.e.pMat[c]) + "\n")
