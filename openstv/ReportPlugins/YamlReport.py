"Plugin module for generating a YAML report."

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

class YamlReport(ReportPlugin):
  "Return a YAML  report."

  status = 0
  reportName = "YAML"
  
  def __init__(self, e, outputFile=None, test=False):
    ReportPlugin.__init__(self, e, outputFile, test)
    
    if self.e.methodName == "Condorcet":
      raise RuntimeError, "YAML report not available for Condorcet elections."

  def generateHeader(self):
    winners = list(self.e.winners)
    winners.sort()
    header = "---\nWinners: %s\nRound:\n" % str(winners)
    self.output(header)
    
  def generateReportNonIterative(self):

    self.generateHeader()

    tally = str([self.e.displayValue(x) for x in self.e.count] + 
                [self.e.displayValue(self.e.exhausted)])
    won = list(self.e.winners)
    won.sort()
    won = str(won)
    lost = list(self.e.losers)
    lost.sort()
    lost = str(lost)
    xfer = "[]"

    roundLine = """\
 -
  Stage: %d
  Tally: %s
  Won:   %s
  Lost:  %s
  Xfer:  %s
""" % (1, tally, won, lost, xfer)
    
    self.output(roundLine)

  def generateReportIterative(self):

    self.generateHeader()

    for r in range(self.e.numRounds):
      roundStage = r
      if self.e.methodName == "ERS97 STV":
        roundStage = self.e.roundToStage(r)
      
      index = str(roundStage + 1)
      tally = ", ".join([self.e.displayValue(x) for x in self.e.count[r]] + 
                  [self.e.displayValue(self.e.exhausted[r])])
      tally = "[" + tally + "]"
      won = [c for c in range(self.e.b.numCandidates)
             if self.e.wonAtRound[c] == r]
      won.sort()
      won = str(won)
      lost = []
      if (r < self.e.numRounds - 1) and self.e.roundInfo[r+1]["action"][0] == "eliminate":
        lost = self.e.roundInfo[r+1]["action"][1] 
        lost.sort()
        lost = str(lost)
      xfer = []
      if (r < self.e.numRounds - 1) and self.e.roundInfo[r+1]["action"][0] == "surplus":
        xfer = self.e.roundInfo[r+1]["action"][1] 
        xfer.sort()
        xfer = str(xfer)
  
      roundLine = """\
 -
  Stage: %s
  Tally: %s
  Won:   %s
  Lost:  %s
  Xfer:  %s
""" % (index, tally, won, lost, xfer)
      self.output(roundLine)
