"Plugin module for QPQ"

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

__revision__ = "$Id: QPQ.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import Iterative
from openstv.plugins import MethodPlugin
from openstv.qx import QX

##  Procedure (from Woodall paper http://www.votingmatters.org.uk/ISSUE17/I17P1.PDF)
##
##  1. Set each candidate to hopeful
##  2. Each ballot has elected 0 candidates
##     Round:
##  3. Calculate quotient qc (count) of each hopeful candidate c
##       qc = vc/(1+tc)
##     where vc is number of ballots ranking C first
##     tc is sum of all fractional numbers of candidates those ballots
##     have so far elected
##  4. Quota Q = va/(1+s-tx)
##     where va is number of active ballots (ballots with hopeful candidate(s))
##     s is total number of seats to be filled
##     tx is sum of fractional number of candidates elected by all inactive ballots
##  5a. Elect candidate with highest quotient if quotient > quota
##      update contribution of ballots contributing to c
##      to 1/qc
##  5b. If no candidate elected in 5a, exclude hopeful with smallest quotient
##  6. Count ends when no hopeful candidates remain

##################################################################

class QPQ(Iterative, MethodPlugin):
  "Quota Preferential by Quotient (QPQ)"

  methodName = "QPQ"
  longMethodName = "Quota Preferential by Quotient"
  onlySingleWinner = False
  threshMethod = True
  status = 2

  htmlBody = """
<p>Quota Preferential by Quotient (QPQ) is a proportional system
that, like STV, meets the <i>Droop proportionality criterion</i>.</p>

<p>For details, see Douglas Woodall's paper,
"QPQ, a quota-preferential STV-like election rule",
<i>Voting matters</i> Issue 17, p1-7 (October 2003)
&lt;http://www.votingmatters.org.uk/ISSUE17/I17P1.PDF&gt;.</p>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    Iterative.__init__(self, b)
    MethodPlugin.__init__(self)
    self.threshName = ["Droop", "Dynamic", "Fractional"]
    self.prec = 10
    self.weakTieBreakMethod = "strong"  # treat all ties as strong
    self.optRestart = True              # option: restart after exclusion
    self.stopCond = ["Continuing Empty"]
    self.va = []         # va[r] is number of active ballots at round r
    self.vc = []         # vc[r][c] is candidate c's votes at round r
    # satisfy reporter
    self.exhausted = []
    self.surplus = []
    self.tc = []         # tc[r][c] is candidate c's ballots' contributions at round r
    self.tx = []         # tx[r] is contribution of inactive ballots at round r
    self.thresh = []     # thresh[r] is the winning quota at round r
    self.votes = []      # votes[c] stores the indices of all votes for candidate c.
    self.restart = False

  def preCount(self):
    "QPQ pre-count"
    Iterative.preCount(self)

    QX.set_precision(self, self.prec)
    QX.set_guard(self, self.prec)

    self.R = 0           # current round
    self.numRounds = 0     # total number of rounds
    self.msg = []        # msg[r] contains text describing round r
    self.count = []      # count[r][c] is candidate c's quotient qc at round r

    for c in range(self.b.numCandidates):
      self.votes.append([])

  def displayValue(self, value):
    "Format a value with specified precision."

    return QX.str(value)

  def allocateRound(self):
    "Allocate space for all data structures for one round."

    self.msg.append("")
    self.roundInfo.append({})
    self.vc.append([0] * self.b.numCandidates)
    self.tc.append([0] * self.b.numCandidates)
    self.count.append([0] * self.b.numCandidates)
    self.tx.append(0)
    self.va.append(0)
    self.thresh.append(0)
    # satisfy reporter
    self.exhausted.append(0)
    self.surplus.append(0)

  def findTiedCand(self, cList, mostfewest, function):
    "Return a list of candidates tied for first or last."

    assert(mostfewest in ["most", "fewest"])
    assert(len(cList) > 0)
    cList = list(cList)
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

  def updateWinners(self):
    "Find best winning candidate."

    desc = ""
    best = 0
    winners = set()
    self.restart = False
    for c in self.continuing:
      if QX.gt(self.count[self.R][c], best):
        winners = set([c])
        best = self.count[self.R][c]
      elif self.count[self.R][c] == best:
        winners.add(c)

    if (len(winners) != 0 and QX.gt(best, self.thresh[self.R])):
      # determine single winner
      (cWin, desc) = self.breakWeakTie(self.R, winners, "most", "winner")
      desc = self.newWinners([cWin])
      self.roundInfo[self.R]["action"] = ("surplus", [cWin])
      # distribute ballots to next choice
      for i in self.votes[cWin][:]:
        self.b.contrib[i] = self.b.getWeight(i) * QX.div(QX.One, self.count[self.R][cWin])
        c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
        if c is not None:
          self.votes[c].append(i)
      self.votes[cWin] = []
    else:
      # if no winner, exclude one candidate
      (elimList, desc) = self.selectCandidatesToEliminate()
      self.roundInfo[self.R]["action"] = ("eliminate", elimList)
      cLose = elimList[0]
      # distribute ballots to next choice
      for i in self.votes[cLose][:]:
        c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
        if c is not None:
          self.votes[c].append(i)
      self.votes[cLose] = []
      self.restart = self.optRestart
    return desc

  def selectCandidatesToEliminate(self):
    "Choose one candidate to eliminate."

    elimList = []
    (c, desc2) = self.breakWeakTie(self.R, self.continuing, "fewest",
                                      "candidate to eliminate")
    elimList = [c]

    # Put losing candidates in the proper list
    self.newLosers(elimList)
    desc = "Candidate %s is eliminated. " % self.b.joinList([c])
    return (elimList, desc+desc2)

  def initialVoteTally(self):
    "Find initial first place votes."

    # Allocate ballots to candidates based on the first choices.
    self.b.contrib = []
    for i in xrange(self.b.numWeightedBallots):
      c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
      if c is not None:
        self.votes[c].append(i)
      self.b.contrib.append(0)
    self.roundInfo[self.R]["action"] = ("first", [])

  def restartVoteTally(self):
    "Restart election after elimination."

    self.continuing |= self.winners
    self.winners = set()
    self.winnersOver = set()
    self.winnersEven = set()
    self.votes = []
    for c in range(self.b.numCandidates):
      self.votes.append([])
    self.initialVoteTally()
    self.roundInfo[self.R]["action"] = ("restart", [])
    return "Restart count. "

  def updateCount(self):
    "Update quotients."

    # Count contribution of all ballots (will eventually subtract active contributions)
    for i in xrange(self.b.numWeightedBallots):
      self.tx[self.R] += self.b.contrib[i]

    # Count number (vc) and contribution (tc) of active ballots (ranking hopeful candidates);
    # Calculate quotient for each hopeful candidate (qc=count)
    # Count total number of active ballots (va)
    # Adjust tx.
    for c in range(self.b.numCandidates):
      for i in self.votes[c]:
        self.vc[self.R][c] += QX.fix(self.b.getWeight(i))
        self.tc[self.R][c] += self.b.contrib[i]
      self.count[self.R][c] = QX.div(self.vc[self.R][c], QX.One + self.tc[self.R][c])
      self.va[self.R] += self.vc[self.R][c]
      self.tx[self.R] -= self.tc[self.R][c]

    # Calculate quota for current round
    self.thresh[self.R] = QX.div(self.va[self.R], QX.fix(1 + self.numSeats) - self.tx[self.R])

  def countBallots(self):
    "Count the votes with QPQ."

    # Do the rounds...
    while (not self.electionOver()):

      self.allocateRound()
      if (self.R == 0):
        self.initialVoteTally()
        self.msg[self.R] = "Count of first choices. "
      elif (self.restart):
        self.msg[self.R] += self.restartVoteTally()

      self.updateCount()
      self.msg[self.R] += self.updateWinners()
      self.R += 1

  def postCount(self):
    "Report QX stats if enabled"
    self.numRounds = self.R
    if False:
      QX.postCount(self, self.R)
