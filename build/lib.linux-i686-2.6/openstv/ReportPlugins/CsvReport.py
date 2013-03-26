"Module for generating reports of election results."

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

__revision__ = "$Id: report.py 570 2009-08-20 17:46:56Z jeff.oneill $"

import string

from openstv.version import v as OpenSTV_version
from openstv.plugins import ReportPlugin

##################################################################

class CsvReport(ReportPlugin):
  "Return a concise table of election results in CSV format."

  status = 1
  reportName = "csv"
  
  def __init__(self, e, outputFile=None, test=False):
    ReportPlugin.__init__(self, e, outputFile, test)
    if self.e.methodName == "Condorcet":
      raise RuntimeError, "CSV report not available for Condorcet elections."
    
  def generateHeader(self):

    if self.test:
      today = ""
      v = ""
    else:
      from datetime import date
      today = date.today().strftime("%d %b %Y")
      v = OpenSTV_version

    if self.e.methodName == "ERS97 STV":
      quota = self.e.displayValue(self.e.quota[-1])
    elif self.e.threshMethod:
      quota = self.e.displayValue(self.e.thresh[-1])
    else:
      quota = self.e.displayValue(0)

    header = """\
"Election for","%s"
"Date","%s"
"Number to be elected",%d
"Valid votes",%d
"Invalid votes",%d
"Quota",%s
"OpenSTV","%s"
"Election rules","%s"
""" % (self.e.title, today, self.e.numSeats, self.cleanB.numBallots,
        self.dirtyB.numBallots - self.cleanB.numBallots, quota, v, 
        self.e.longMethodName)

    self.output(header)

  def generateReportNonIterative(self):
    "Return a results sheet in the CVS format used by the ERS."

    self.generateHeader()
    
    out = self.output

    out("""\
,
,"First"
"Candidates","Preferences"
""")

    # candidate lines
    for c in range(len(self.dirtyB.names)):
      line = ""
      if c in self.dirtyB.withdrawn:
        # Withdrawn candidates appear in the results even though there is
        # nothing to report.  Handle them separately.
        line += '"%s","Withdrawn",\n' % (self.dirtyB.names[c])
        
      else:
        # Since we are looping over all candidates, need to convert the index
        # into the list of non-withdrawn candidates.
        name = self.dirtyB.names[c]
        cc = self.cleanB.names.index(name)
        line += '"%s",%d,' % (self.cleanB.names[cc], 1.0*self.e.count[cc]/self.e.p)
        if cc in self.e.winners:
          line += '"Elected"'
        line += '\n'
      out(line)

    # non-transferable and totals
    out('"Non-transferable", ,\n')
    out('"Totals",' + str(self.cleanB.numBallots) + '\n')

  def generateReportIterative(self):
    "Return a results sheet in the CVS format used by the ERS."

    self.generateHeader()
    
    fmt = "%+." + str(self.e.prec) + "f"

    if self.e.methodName == "ERS97 STV":
      nRS = self.e.numStages
    else:
      nRS = self.e.numRounds

    # title lines
    tl1 = ','
    tl2 = ',"First"'
    tl3 = '"Candidates","Preferences"'
    for RS in range(1, nRS):
      tl1 += ',"Stage",%d' % (RS+1)

      if self.e.methodName == "ERS97 STV":
        R = self.e.stages[RS][-1]
      else:
        R = RS

      if self.e.methodName == "Bucklin":
        tl2 += ',"",'
        tl3 += ',"",'
      elif self.e.roundInfo[R]["action"][0] == "surplus":
        tl2 += ',"Surplus of",'
        surplus = [self.cleanB.names[c] for c in self.e.roundInfo[R]["action"][1]]
        surplus.sort()
        tl3 += ',"' + string.join(surplus, '+') + '",'
      elif self.e.roundInfo[R]["action"][0] == "eliminate":
        tl2 += ',"Exclusion of",'
        eliminated = [self.cleanB.names[c] for c in self.e.roundInfo[R]["action"][1]]
        eliminated.sort()
        tl3 += ',"' + string.join(eliminated, '+') + '",'
      else:
        assert(0)

    out = self.output
    out(tl1 + '\n')
    out(tl2 + '\n')
    out(tl3 + '\n')

    # candidate lines
    for c in range(len(self.dirtyB.names)):
      if c in self.dirtyB.withdrawn:
        # Withdrawn candidates appear in the results even though there is
        # nothing to report.  Handle them separately.
        line = '"%s","Withdrawn",' % (self.dirtyB.names[c])
        line += ',,' * (nRS-1) + '\n'
        out(line)

      else:

        # Since we are looping over all candidates, need to convert the index
        # into the list of non-withdrawn candidates.
        name = self.dirtyB.names[c]
        cc = self.cleanB.names.index(name)

        line = '"%s",%d,' % (self.cleanB.names[cc],
                                 self.e.count[0][cc]/self.e.p)

        for RS in range(1, nRS):
          if self.e.methodName == "ERS97 STV":
            R = self.e.stages[RS][-1]
            prevround = self.e.stages[RS-1][-1]
          else:
            R = RS
            prevround = RS - 1

          diff = self.e.count[R][cc] - self.e.count[prevround][cc]
          if diff == 0:
            diffstr = ''
          else:
            diffstr = fmt % (1.0*diff/self.e.p)

          count = self.e.count[R][cc]
          if cc in self.e.losers and self.e.lostAtRound[cc] <= R \
                 and count == 0:
            countstr = '"-"'
          else:
            countstr = self.e.displayValue(count)

          line += '%s,%s,' % (diffstr, countstr)

        if cc in self.e.winners:
          line += '"Elected"'
        line += '\n'
        out(line)

    # non-transferable
    line = '"Non-transferable", ,'
    for RS in range(1, nRS):
      if self.e.methodName == "ERS97 STV":
        R = self.e.stages[RS][-1]
        prevround = self.e.stages[RS-1][-1]
      else:
        R = RS
        prevround = RS - 1
      diff = self.e.exhausted[R] - self.e.exhausted[prevround]
      if diff == 0:
        diffstr = ''
      else:
        diffstr = fmt % (1.0*diff/self.e.p)

      exh = self.e.exhausted[R]
      exhstr = self.e.displayValue(exh)

      line += '%s,%s,' % (diffstr, exhstr)
    line += '\n'
    out(line)

    # totals
    line = '"Totals",' + str(self.cleanB.numBallots)
    for RS in range(1, nRS):
      line += ',,%s' % self.e.displayValue(self.cleanB.numBallots*self.e.p)
    line += '\n'
    out(line)
