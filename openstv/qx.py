"Quasi-exact fixed-point arthmetic support"

## Copyright 2009-2010 Jeffrey O'Neill
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

__revision__ = "$Id: qx.py 710 2010-02-22 00:19:20Z jlundell $"

from openstv.STV import RecursiveSTV

#  class QX: quasi-exact fixed-point arithmetic support
#
#  All methods of QX are static.
#  Set precision and guard through setter methods.
#  If guard > 0, then QX will use quasi-exact guarded-precision arithmetic
#  See the appendix of http://www.votingmatters.org.uk/ISSUE24/I24P2.pdf
#    for a brief description of quasi-exact arithmetic
#
#  maxDiff & minDiff are maintained to help determine whether the guard is sufficiently large
#
class QX(object):
  "Fixed-point arithmetic with optional guard digits"
  precision = 6
  guard = 0
  p = 10**(precision+guard)
  g = 10**guard
  grnd = g/2
  geps = g/10
  One = p
  Epsilon = 1
  maxDiff = 0
  minDiff = p * 100

  @staticmethod
  def set_precision(e, v):
    "set precision in decimal digits"
    QX.precision = v
    QX.p = 10 ** (QX.precision + QX.guard)
    e.p = QX.p	# for report.py
    QX.One = QX.p
    QX.maxDiff = 0
    QX.minDiff = QX.p * 100

  @staticmethod
  def set_guard(e, v):
    "set number of decimal guard digits"
    QX.guard = v
    QX.g = 10 ** QX.guard
    QX.grnd = QX.g/2
    QX.geps = QX.g/10
    QX.set_precision(e, QX.precision)

  @staticmethod
  def fix(a):
    "convert int to fixed point"
    return a * QX.p

  @staticmethod
  def eq(a, b):
    "return True if a == b; else False"
    if (QX.guard == 0):
      return a == b
    gdiff = abs(a - b)
    if gdiff < QX.geps and gdiff > QX.maxDiff:
      QX.maxDiff = gdiff
    if gdiff >= QX.geps and gdiff < QX.minDiff:
      QX.minDiff = gdiff
    return abs(a - b) < QX.geps

  @staticmethod
  def lt(a, b):
    "return True if a < b; else False"
    return (a < b) and (QX.guard == 0 or not QX.eq(a, b))

  @staticmethod
  def gt(a, b):
    "return True if a > b; else False"
    return (a > b) and (QX.guard == 0 or not QX.eq(a, b))

  @staticmethod
  def le(a, b):
    "return True if a <= b; else False"
    return (a <= b) or (QX.guard != 0 and QX.eq(a, b))

  @staticmethod
  def ge(a, b):
    "return True if a >= b; else False"
    return (a >= b) or (QX.guard != 0 and QX.eq(a, b))

  @staticmethod
  def mult(a, b):
    "multiply two fixed-point numbers"
    return a * b / QX.p

  @staticmethod
  def div(a, b):
    "divide two fixed-point numbers"
    return (a * QX.p) / b

  @staticmethod
  def add(a, b):
    "add two fixed-point numbers (for completeness)"
    return a + b

  @staticmethod
  def sub(a, b):
    "subtract two fixed-point numbers (for completeness)"
    return a - b

  @staticmethod
  def str(v):
    "stringify a fixed-point value"
    if QX.p == 0:
      return str(v)
    nfmt = "%d.%0" + str(QX.precision) + "d" # %d.%0_d
    gv = (v + QX.grnd)/QX.g	              # round off guard digits
    return nfmt % (gv/(QX.p/QX.g), gv%(QX.p/QX.g))

  @staticmethod
  def postCount(e, R):
    "Report QX statistics"
    e.msg.append("")
    e.msg[R] = """\
maxDiff: %d  (s/b << geps)
geps:    %d
minDiff: %d  (s/b >> geps)
guard:   %d
prec:    %d

""" % (
      QX.maxDiff,
      QX.geps,
      QX.minDiff,
      QX.g,
      QX.p
      )

##################################################################

class RecursiveQXSTV(RecursiveSTV):
  """Class that reimplements recursive methods using QX (quasi-exact) arithmetic.
  
  No additional attributes.
  """

  def __init__(self, b):
    RecursiveSTV.__init__(self, b)
    self.prec = 9
    self.strongTieBreakMethod = "random" # break all ties randomly
    self.weakTieBreakMethod = "strong"	# treat all ties as strong
    self.surplusLimit = QX.Epsilon
    
    #  A note for debugging via print:
    #  comment out the sys.stderr assignment in Frame.__init__
    #  and then print to stderr thus to send output to terminal:
    #  print >> sys.stderr, "MeekQX: prec:", prec, "ties:", strongTieBreakMethod
    #

  def preCount(self):
    RecursiveSTV.preCount(self)

    QX.set_precision(self, self.prec)
    QX.set_guard(self, self.prec)

  def displayValue(self, value):
    "RecursiveQXSTV: Format a value with specified precision."

    return QX.str(value)

  def updateThresh(self):
    "RecursiveQXSTV: Compute the value of the winning threshold."

    threshNum = QX.fix(self.b.numBallots) - self.exhausted[self.R]
    self.thresh[self.R] = threshNum/(self.numSeats + 1)

  def updateWinners(self):
    "RecursiveQXSTV: Find new winning candidates."

    winners = []
    for c in self.continuing:
      if QX.gt(self.count[self.R][c], self.thresh[self.R]):
        winners.append(c)
    if len(winners) > 0:
      self.roundInfo[self.R]["winners"] = self.newWinners(winners)

  def isSurplusToTransfer(self):
    """RecursiveQXSTV: Decide whether to transfer surplus votes or eliminate 
    candidates."""
    
    if ( QX.eq(self.surplus[self.R-1], 0) or
         (self.delayedTransfer == "On" and len(self.getSureLosers()) != 0) ):
      return False
    else:
      return True
    
  def getSureLosers(self, R=None):
    "RecursiveQXSTV: Return all candidates who are sure losers."

    # Return all candidates who are sure losers but do not look at previous
    # rounds to break ties.

    if R is None: 
      R = self.R - 1
      
    maxNumLosers = len(self.continuing) + len(self.winners) - self.numSeats
    assert(maxNumLosers < len(self.continuing))
    losers = []

    # We need to make sure that all candidates with the same number of votes
    # are treated the same, so group candidates with the same number of votes
    # together and sort clusters in order of votes (fewest first).
    continuing = list(self.continuing)
    continuing.sort(key=lambda a, f=self.count[R]: f[a])
    clusteredContinuing = [[continuing[0]]]
    for c in continuing[1:]:
      if QX.eq(self.count[R][c], self.count[R][ clusteredContinuing[-1][0] ]):
        clusteredContinuing[-1].append(c)
      else:
        clusteredContinuing.append([c])

    s = self.surplus[R]
    potentialLosers = []
    for i, cluster in enumerate(clusteredContinuing[:-1]):
      currentClusterCount = self.count[R][ cluster[0] ]
      nextClusterCount = self.count[R][ clusteredContinuing[i+1][0] ]
      s += len(cluster) * currentClusterCount
      potentialLosers += cluster
      
      if QX.lt(s, nextClusterCount) and len(potentialLosers) <= maxNumLosers:
        losers = potentialLosers[:]
        
    return losers

  def findTiedCand(self, cList, mostfewest, function):
    "RecursiveQXSTV: Return a list of candidates tied for first or last."

    assert(mostfewest in ["most", "fewest"])
    assert(len(cList) > 0)
    tiedCand = []

    # Find a candidate who is winning/losing.  He may be tied with others.
    if mostfewest == "most":
      cList.sort(key=lambda a, f=function: -f[a])
    elif mostfewest == "fewest":
      cList.sort(key=lambda a, f=function: f[a])
    top = cList[0] # first/last place candidate

    # Find the number of candidates who are tied with him.
    for c in cList:
      if QX.eq(function[c], function[top]):
        tiedCand.append(c)

    return tiedCand

  def updateKeepFactors(self):
    "RecursiveQXSTV: Udpate the candidate keep factors."

    if len(self.winners) != 0:
      desc = "Keep factors of candidates who have exceeded the threshold: "
      winners = []
    else:
      desc = ""

    candidateList = list(self.continuing | self.winners)
    candidateList.sort()
    for c in candidateList:
      if QX.gt(self.count[self.R-1][c], self.thresh[self.R-1]):
        self.roundInfo[self.R]["action"][1].append(c)
        kf, rem = divmod(self.keepFactor[self.R-1][c] * self.thresh[self.R-1],
                      self.count[self.R-1][c])
        if rem > 0: 
          kf += QX.Epsilon
        self.keepFactor[self.R][c] = kf
        winners.append("%s, %s"\
                       % (self.b.names[c],
                          self.displayValue(self.keepFactor[self.R][c]))
                       )
      else:
        self.keepFactor[self.R][c] = self.keepFactor[self.R-1][c]

    if len(self.winners) != 0:
      desc += self.b.joinList(winners, convert="none") + ". "
    return desc

  def postCount(self):
    "RecursiveQXSTV: Report QX stats if enabled"
    RecursiveSTV.postCount(self)
    if False:
      QX.postCount(self, self.R+1)
