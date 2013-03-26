"Plugin module for generating a concise report in text format."

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

import textwrap
import math
import os

from openstv.version import v as OpenSTV_version
from openstv.plugins import ReportPlugin

##################################################################

class TextReport(ReportPlugin):
  "Return a concise table of election results in text format."

  status = 1
  reportName = "text"
  
  def __init__(self, e, maxWidth=79, style="full", outputFile=None, test=False):
    ReportPlugin.__init__(self, e, outputFile, test)

    assert(style in ["full", "table", "round"])
    self.maxWidth = maxWidth
    self.style = style
    self.maxColWidth = 0
    self.prtf = None

  def format(self, value):
    return self.pipify( self.e.displayValue( value ) )
  
  def pipify(self, value):
    """Surround text with pipe"""
    return ("|" + self.prtf) % value
  
  def printTableRow(self, values,width, nSubCol):
    """Print one 'line' of results--might occupy more than one line of text."""
    # Separator line
    self.output( "=" * width + "\n" )
    line = values.pop(0)
    for (index,value) in enumerate(values):
      if ((index % nSubCol == 0) and index > 0): 
        line += "\n  "
      line += ("|" + self.prtf) % value
    line += "\n"
    self.output(line)
  
  def generateWithdrawnText(self):

    # Create description of withdrawn candidates
    if len(self.dirtyB.withdrawn) == 0:
      withdrawnText = "No candidates have withdrawn."
    elif len(self.dirtyB.withdrawn) == 1:
      withdrawnText = "Removed withdrawn candidate %s from the ballots."\
                          % self.dirtyB.withdrawn[0]
    else:
      self.dirtyB.withdrawn.sort()
      withdrawnText = "Removed withdrawn candidates %s from the ballots."\
                          % self.dirtyB.joinList(self.dirtyB.withdrawn)
    withdrawnText = textwrap.fill(withdrawnText, width=self.maxWidth)
    
    return withdrawnText

  def generateHeader(self):
  
    header = "OpenSTV version %s (http://www.OpenSTV.org/)\n\n" % \
           ("" if self.test else OpenSTV_version)

    # Don't want to modify all of the ref files for this as I'll probably
    # be reworking testing after this release.
    if not self.test:
      header += """\
Suggested donation for using OpenSTV for an election is $50.  Please go to 
http://www.OpenSTV.org/donate to donate via PayPal, Google Checkout, or
Amazon Payments.  

Certified election reports are also available.  Please go to 
http://www.openstv.org/certified-reports for more information.

"""
    
    if self.dirtyB.getFileName() is not None:
      header += "Loading ballots from file %s.\n" % \
             os.path.basename(self.dirtyB.getFileName())
    header += """\
Ballot file contains %d candidates and %d ballots.
%s
Ballot file contains %d non-empty ballots.

Counting votes for %s using %s.
%d candidates running for %d seat%s.
""" % (self.dirtyB.numCandidates, self.dirtyB.numBallots,
       self.generateWithdrawnText(),
       self.cleanB.numBallots,
       self.e.title, self.e.longMethodName,
       self.cleanB.numCandidates, self.e.numSeats, 
       "s" if self.e.numSeats > 1 else ""
       )
    self.output( header )
    if self.e.optionsMsg != "":
      self.output( textwrap.fill(self.e.optionsMsg, width=self.maxWidth) + "\n" )
    self.output( "\n" )

  def setMinColWidth(self, minColWidth=4):

    # Find the largest value to appear in the report
    mv = 0
    if self.e.methodName == "Condorcet":
      for i in range(self.cleanB.numCandidates):
        m = max(self.e.pMat[i])
        mv = max(m, mv)

    elif self.e.methodName == "Borda":
      m = max(self.e.count)
      mv = max(m, mv)

    elif self.e.iterative:
      if "exhausted" in dir(self.e):
        m = max(self.e.exhausted)
        mv = max(m, mv)
      if "thresh" in dir(self.e):
        m = max(self.e.thresh)
        mv = max(m, mv)
      if "surplus" in dir(self.e):
        m = max(self.e.surplus)
        mv = max(m, mv)
      for i in range(len(self.e.count)):
        m = max(self.e.count[i])
        mv = max(m, mv)
        
    else:
      if "exhausted" in dir(self.e):
        mv = max(self.e.exhausted, mv)
      if "thresh" in dir(self.e):
        mv = max(self.e.thresh, mv)
      if "surplus" in dir(self.e):
        mv = max(self.e.surplus, mv)
      m = max(self.e.count)
      mv = max(m, mv)
       
    # From the max value, compute the minimum column width needed
    mv /= self.e.p
    self.maxColWidth = int(math.floor(math.log10(mv))) + 1
    if self.e.prec > 0:
      self.maxColWidth += self.e.prec + 1
    self.maxColWidth = max(self.maxColWidth, minColWidth)

  def setPrintField(self, cw):
    self.prtf = "%" + str(cw) + "." + str(cw) + "s"  # %_._s

  def generateMatrix(self, matrix):
    "Return a matrix in text format."

    nCol = self.cleanB.numCandidates

    txt = self.prtf % ""

    # Candidate names
    for c in range(self.cleanB.numCandidates):
      txt += self.pipify( self.cleanB.names[c] )
    txt += "\n"

    # Separator line
    txt += "-"* self.maxColWidth + ("+" + "-" * self.maxColWidth )*nCol + "\n"

    # For each row, candidate name and matrix values
    for c in range(self.cleanB.numCandidates):
      txt += self.prtf % self.cleanB.names[c]
      for d in range(self.cleanB.numCandidates):
        txt += self.format( matrix[c][d] )
      txt += "\n"
      
    return txt
  
  def generateReportCondorcet(self):
    "Generate a text report for an election using Condorcet."

    self.setMinColWidth()
    self.setPrintField(self.maxColWidth)
    self.generateHeader()
    report = """\
Pairwise Comparison Matrix:

%s
Smith Set: %s

""" % (self.generateMatrix(self.e.pMat),
       self.cleanB.joinList(self.e.smithSet),
       )
    self.output( report )

    if len(self.e.smithSet) == 1:
      self.output("No completion necessary since the Smith set "\
             "has just one candidate.\n")
      
    elif self.e.completion == "Schwartz Sequential Dropping":
      completionMsg = """\
Using Schwartz sequential dropping to choose the winner.
Matrix of beatpath magnitudes:

%s%s

""" % (self.generateMatrix(self.e.dMat), self.e.SSDinfo)
      self.output(completionMsg)
    elif self.e.completion == "IRV on Smith Set":
      self.output("Using IRV to choose the winner from the Smith set.\n\n")
      R = TextReport(self.e.e, self.maxWidth, "table", outputFile = self.outputFile)
      R.generateReport()
      self.output("\n")
    elif self.e.completion == "Borda on Smith Set":
      self.output("Using the Borda count to choose the winner "\
            "from the Smith set.\n\n")
      R = TextReport(self.e.e, self.maxWidth, "table", outputFile = self.outputFile)
      R.generateReport()
      self.output("\n")
    self.output(self.getWinnerText(self.e.winners) + "\n")

  def generateTextRoundResults(self, R, width, nSubCol):
    self.printTableRow( self.getValuesForRound( R ), width, nSubCol)
    ## Print message.
    self.output( "  |" + "-" * (width-3) + "\n")
    line = textwrap.fill(self.e.msg[R], initial_indent="  | ",
                         subsequent_indent="  | ", width=width)
    self.output( line + "\n" )

  def generateReportNonIterative(self):
    "Pretty print results in text format."

    self.setMinColWidth(5)
    self.setPrintField(self.maxColWidth)
    out = self.output

    # Include summary information for full results.
    if self.style == "full":
      self.generateHeader()
    
    # Find length of longest candidate name
    maxNameLen = 9 # 9 letters in "Exhausted"
    for c in range(self.cleanB.numCandidates):
      maxNameLen = max(maxNameLen, len(self.cleanB.names[c]))

    # Print format strings
    fmt1 = "%" + str(maxNameLen) + "." + str(maxNameLen) + "s"  # %_._s
    fmt2 = "%" + str(self.maxColWidth) + "." + str(self.maxColWidth) + "s"  # %_._s

    # Header
    out( (fmt1 + " | " + fmt2 + "\n") % ("Candidate", "Count") )
    out("=" * (maxNameLen + 3 + self.maxColWidth) + "\n")

    # Candidate vote totals for the round
    for c in range(self.cleanB.numCandidates):
      out( (fmt1 + " | " + fmt2 + "\n") %\
             (self.cleanB.names[c],
              self.e.displayValue(self.e.count[c])))

    # Exhausted ballots
    out((fmt1 + " | " + fmt2 + "\n") % ("Exhausted", self.e.exhausted) )

    # Messages
    out("\n")
    line = textwrap.fill(self.e.msg, width=self.maxWidth)
    line += "\n\n"
    out(line)

    # Include winners for full results
    if self.style == "full":
      out( self.getWinnerText(self.e.winners, self.maxWidth))

  def generateReportIterative(self, R=None):
    "Pretty print results in text format."
    
    self.setMinColWidth()
    out = self.output

    # The following determines the actual column width to use that
    # makes the table ouput compact and evenly distributed

    # nCol is the total number of columns
    nCol = self.cleanB.numCandidates
    nCol += 1 # Exhausted
    if self.e.threshMethod:
      nCol += 1 # Surplus
      nCol += 1 # Thresh
    # maxnSubCol is the maximum number of columns that can fit in a
    # single row.  This is used to determine how many rows we need.
    maxnSubCol = (self.maxWidth-2)/(self.maxColWidth+1)
    # nRow is the number of rows needed to display all of the columns    
    (nRow, r) = divmod(nCol, maxnSubCol)
    if r > 0: 
      nRow += 1
    # nSubCol is the number of columns per row (distrubted evenly across rows)
    (nSubCol, r) = divmod(nCol, nRow)
    if r > 0: 
      nSubCol += 1
    # colWidth is the width of a column in characters
    colWidth = (self.maxWidth-2)/nSubCol - 1
    # width is the actual width of the table
    width = 2 + nSubCol*(colWidth+1)

    # Find length of longest string in the table header
    maxNameLen = 9 # 9 letters in "Exhausted"
    for c in range(self.cleanB.numCandidates):
      maxNameLen = max(maxNameLen, len(self.cleanB.names[c]))

    # Pad strings for table header to a multiple of colWidth
    maxNameLen += colWidth - (maxNameLen % colWidth)
    header = []
    for c in range(self.cleanB.numCandidates):
      header.append(self.cleanB.names[c].ljust(maxNameLen))
    header.append("Exhausted".ljust(maxNameLen))
    if self.e.threshMethod:
      header.append("Surplus".ljust(maxNameLen))
      header.append("Threshold".ljust(maxNameLen))

    # nSubRow is the number of rows needed to display the full candidate names
    (nSubRow, r) = divmod(maxNameLen, colWidth)
    if r > 0: 
      nSubRow += 1

    self.setPrintField(colWidth)

    # Include summary information for full results.
    if self.style == "full":
      self.generateHeader()

    if self.style in ["full", "table"]:
      # Table header
      for r in range(nRow):
        for sr in range(nSubRow):
          line = ""
          if r == 0 and sr == 0:
            line += " R"
          else:
            line += "  "
          b = sr*colWidth
          e = b + colWidth

          for sc in range(nSubCol):
            h = r*nSubCol + sc
            if h == len(header): 
              break
            line += ( "|" + header[h][b:e] )
          out(line + "\n")
        
        if r < nRow-1:
          out("  |" + ("-" * colWidth + "+" ) *(nSubCol-1) + "-" *colWidth + "\n")
        
      # Rounds
      for R in range(self.e.numRounds):
        self.generateTextRoundResults(R, width, nSubCol)
      out("\n")

    # Include winners for full results
    if self.style == "full":
      out( self.getWinnerText(self.e.winners, width) )

    # Generate results for only the specified round
    if self.style == "round":
      self.generateTextRoundResults(R, width, nSubCol)

    # Add optional post-count information
    if len(self.e.msg) > self.e.numRounds:
      out("\n\n")
      out(self.e.msg[self.e.numRounds])
