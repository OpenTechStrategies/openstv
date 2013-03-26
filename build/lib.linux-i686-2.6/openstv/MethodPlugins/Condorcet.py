"Plugin module for Condorcet"

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

__revision__ = "$Id: Condorcet.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import NonIterative
from openstv.plugins import MethodPlugin
from openstv.MethodPlugins.Borda import Borda
from openstv.MethodPlugins.IRV import IRV

##################################################################

class Condorcet(NonIterative, MethodPlugin):
  "Implement Condorcet voting with several options for completion methods"
  
  methodName = "Condorcet"
  longMethodName = "Condorcet Voting"
  onlySingleWinner = True
  status = 1

  htmlBody = """
<p>Condorcet voting elects the candidate who wins all pairwise
elections against the other candidates.  In relatively rare
situations, a cycle will occur where no Condorcet winner exists (i.e.,
every candidte is beaten by at least one other candidate).  The set
of candidates in the cycle is called the Smith set.  In this instance,
a "completion method" is used to choose the winner from the Smith set.
There are three choices for the completion method:</p>

<ul>
<li> Schwartz sequential dropping
<li> Instant runoff voting on the Smith set
<li> Borda count on the Smith set
</ul>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    NonIterative.__init__(self, b)
    MethodPlugin.__init__(self)

    self.completion = "Schwartz Sequential Dropping"
    self.createGuiOptions(["completionMethod"])
    self.e = None
    self.smithSet = []
    self.SSDinfo = ""
    self.pMat = []
    self.dMat = []
    
  def preCount(self):
    NonIterative.preCount(self)

    assert(self.completion in ["Schwartz Sequential Dropping",
                               "IRV on Smith Set",
                               "Borda on Smith Set"])

    self.optionsMsg = "Using %s for the completion method." % self.completion

  def computePMat(self):
    "Compute the pairwise comparison matrix."

    # Intialize space
    self.pMat = []
    for c in range(self.b.numCandidates):
      self.pMat.append([0] * self.b.numCandidates)

    # Compute pMat
    for i in xrange(self.b.numWeightedBallots):
      weight, ballot = self.b.getWeightedBallot(i)
      remainingC = range(self.b.numCandidates)
      for c in ballot:
        remainingC.remove(c)
        for d in remainingC:
          self.pMat[c][d] += weight

  def computeSmithSet(self):
    "Compute the Smith set."

    dMat = []
    for c in range(self.b.numCandidates):
      dMat.append([0] * self.b.numCandidates)

    # compute the Smith set
    # Adapted from code posted by Markus Schulze at
    # http://groups.yahoo.com/group/election-methods-list/message/6493
    self.smithSet = range(self.b.numCandidates)
    for c in range(self.b.numCandidates):
      for d in range(self.b.numCandidates):
        if c != d:
          if self.pMat[c][d] >= self.pMat[d][c]:
            dMat[c][d] = True
          else:
            dMat[c][d] = False
    for c in range(self.b.numCandidates):
      for d in range(self.b.numCandidates):
        if c != d:
          for k in range(self.b.numCandidates):
            if c != k and d != k:
              if dMat[d][c] and dMat[c][k]:
                dMat[d][k] = True
    for c in range(self.b.numCandidates):
      for d in range(self.b.numCandidates):
        if c != d:
          if ( (not dMat[c][d]) and
               dMat[d][c] and
               (c in self.smithSet) ):
            self.smithSet.remove(c)
    self.smithSet.sort()

  def SchwartzSequentialDropping(self):
    "Complete with SSD."

    # Initialize the defeats matrix: dMat[i][j] gives the magnitude of i's
    # defeat of j. If i doesn't defeat j, then dMat[i][j] == 0.
    self.dMat = []
    for c in range(self.b.numCandidates):
      self.dMat.append([0] * self.b.numCandidates)

    for c in range(self.b.numCandidates):
      for d in range(self.b.numCandidates):
        self.dMat[c][d] = self.pMat[c][d]
    for c in range(self.b.numCandidates):
      for d in range(c):
        if self.pMat[c][d] > self.pMat[d][c]: 
          self.dMat[d][c] = 0
        if self.pMat[c][d] < self.pMat[d][c]: 
          self.dMat[c][d] = 0
        if self.pMat[c][d] == self.pMat[d][c]: 
          self.dMat[c][d] = self.dMat[d][c] = 0

    # Determine "beatpath" magnitudes array: dMat[i][j] will be the
    # maximum beatpath magnitudes array. The i,j entry is the greatest
    # magnitude of any beatpath from i to j. A beatpath's magnitude is
    # the magnitude of its weakest defeat.

    changing = 1
    while changing:
      changing = 0
      for c in range(self.b.numCandidates):
        for d in range(self.b.numCandidates):
          for k in range(self.b.numCandidates):
            dmin = min (self.dMat[c][d], self.dMat[d][k])
            if self.dMat[c][k] < dmin:
              self.dMat[c][k] = dmin
              changing = 1

    ctng = range(self.b.numCandidates)[:]
    for c in ctng[:]:
      for d in ctng[:]:
        if self.dMat[d][c] > self.dMat[c][d] and c in ctng:
          ctng.remove(c)

    if len(ctng) > 1:
      ctng.sort()
      self.SSDinfo = """
Candidates remaining after SSD: %s

Tie broken randomly.""" % self.b.joinList(ctng)
      (c0, desc) = self.breakStrongTie(ctng)
    else:
      self.SSDinfo = ""
      c0 = ctng[0]

    return c0

  def countBallots(self):
    "Count the votes using Condorcet voting."

    # self.pMat[i][j]: number of votes ranking candidate i over candidate j
    self.computePMat()

    # Even though the Smith Set isn't needed for all completion methods
    # it provides interesting info, so compute it always.
    self.computeSmithSet()

    if len(self.smithSet) == 1:
      c0 = self.smithSet[0]
    else:
      # Do the completion
      if self.completion == "Schwartz Sequential Dropping":
        c0 = self.SchwartzSequentialDropping()
      elif self.completion in ["IRV on Smith Set", "Borda on Smith Set"]:
        # Copy ballots and get rid of candidates not in Smith set
        withdrawList = []
        for c in range(self.b.numCandidates):
          if (c not in self.smithSet):
            withdrawList.append(c)
        dirtyBallots = self.b.copy()
        dirtyBallots.withdrawn = withdrawList
        dirtyBallots.numSeats = 1
        cleanBallots = dirtyBallots.getCleanBallots()
        if self.completion == "IRV on Smith Set":
          self.e = IRV(cleanBallots)
          self.e.strongTieBreakMethod = self.strongTieBreakMethod
          self.e.runElection()
        elif self.completion == "Borda on Smith Set":
          self.e = Borda(cleanBallots)
          self.e.strongTieBreakMethod = self.strongTieBreakMethod
          self.e.runElection()
        assert(len(self.e.winners) == 1)
        # The Smith set is sorted.  The winner just determined is the index
        # of the winner in the Smith set.
        cIndex = list(self.e.winners)[0]
        c0 = self.smithSet[cIndex]
      else:
        assert(0)

    self.winners = set([c0])
