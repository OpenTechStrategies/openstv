"Plugin module for generating a concise report in HTML format."

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

import os

from openstv.plugins import ReportPlugin
from openstv.version import v as OpenSTV_version

##################################################################

class HtmlReport(ReportPlugin):
  "Return a concise table of election results in HTML format."
  
  status = 1
  reportName = "html"
    
  def __init__(self, e, outputFile=None, test=False):
    ReportPlugin.__init__(self, e, outputFile, test)
    if self.e.methodName == "Condorcet":
      raise RuntimeError, "HTML report not available for Condorcet elections."

  def printTableRow(self, values):
    """Print a single table line"""
    out = self.output
    out("<tr>\n")
    out("<td class='round' rowspan='2'>%s</td>\n" % (values.pop(0)))
    for value in values:
      out("<td>%s</td>\n" % value)
    out("</tr>\n\n")
  
  def generateHeader(self):

    header = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>%s</title>
<style type="text/css" media="screen">
  .rounds, .rounds th, .rounds td { 
        border: solid 1px; 
        border-spacing: 0;
        text-align: right; }
  .rounds th, .rounds td { padding: 1px 3px; }
  td.comment  { 
      font-size: smaller; 
      font-style: italic;
      text-align: left; }
  td.round, .rounds th { text-align: center; }
</style>
</head>
<body>
<h3 class="title">%s</h3>
<p class="overview">
OpenSTV version %s (http://www.OpenSTV.org/)<br>
<br>
Suggested donation for using OpenSTV for an election is $50.  Please go to<br>
http://www.OpenSTV.org/donate to donate via PayPal, Google Checkout, or<br>
Amazon Payments.<br>
<br>
Certified election reports are also available.  Please go to<br>
http://www.openstv.org/certified-reports for more information.<br>
<br>
Loading ballots from file %s.<br>
Ballot file contains %d candidates and %d ballots.<br>
Ballot file contains %d non-empty ballots.<br>
<br>
Counting votes for %s using %s.<br>
%d candidates running for %d seat%s.
</p>
"""  % (self.e.title, self.e.title,
        "" if self.test else OpenSTV_version,
        os.path.basename(self.dirtyB.getFileName()),
        self.dirtyB.numCandidates, self.dirtyB.numBallots,
        self.cleanB.numBallots,
        self.e.title, self.e.longMethodName,
        self.cleanB.numCandidates, self.e.numSeats, 
        "s" if self.e.numSeats > 1 else ""
        )

    self.output(header)
    
  def generateReportNonIterative(self):
    "Pretty print results in html format."

    self.generateHeader()
    
    nCol = self.cleanB.numCandidates
    nCol += 1 # Exhausted
    out = self.output

    out("""\
<table class="rounds" >

<tr>
<th>Round</th>
""")

    for c in range(self.cleanB.numCandidates):
      out("<th>%s</th>\n" % self.cleanB.names[c])
    out("<th>%s</th>\n" % "Exhausted")
    out("</tr>\n\n")
      
    out("<tr>\n")
    out("<td class='round' rowspan='2'>1</td>\n")
    for c in range(self.cleanB.numCandidates):
      out("<td>%s</td>\n" % self.e.displayValue(self.e.count[c]))
    out("<td>%s</td>\n" % self.e.displayValue(self.e.exhausted))
    out("</tr>\n\n")

    out("<tr><td colspan='%d' class='comment'>%s</td></tr>\n\n" % (nCol, self.e.msg))

    out("</table>\n\n")

    # Winners
    winTxt = self.getWinnerText(self.e.winners)
    winTxt = winTxt.replace("\n", "<br>\n")
    out("<p class='winner'>%s</p>\n\n" % winTxt)

    out("</body>\n</html>\n")
    
  def generateReportIterative(self):
    "Pretty print results in html format."

    self.generateHeader()
    
    nCol = self.cleanB.numCandidates
    nCol += 1 # Exhausted
    if self.e.threshMethod:
      nCol += 2 # Surplus and Thresh

    out = self.output

    out("""\
<table class="rounds">

<tr>
<th>Round</th>
""")

    for c in range(self.cleanB.numCandidates):
      out("<th>%s</th>\n" % self.cleanB.names[c])
    out("<th>%s</th>\n" % "Exhausted")
    if self.e.threshMethod:
      out("<th>%s</th>\n" % "Surplus")
      out("<th>%s</th>\n" % "Threshold")
    out("</tr>\n\n")
      
    for R in range(self.e.numRounds):
      self.printTableRow(self.getValuesForRound(R))
      out("<tr><td colspan='%d' class='comment'>%s</td></tr>\n\n" % (nCol, self.e.msg[R]))

    out("</table>\n\n")

    # Winners
    winTxt = self.getWinnerText(self.e.winners)
    out("<p class='winner'>%s</p>\n\n" % winTxt)
    out("</body>\n</html>\n")
