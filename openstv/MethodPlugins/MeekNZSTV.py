"Plugin module for New Zealand Meek STV"

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

__revision__ = "$Id: MeekSTV.py 537 2009-05-16 18:45:21Z jeff.oneill $"

from openstv.STV import RecursiveSTV
from openstv.MethodPlugins.MeekSTV import MeekSTV
from openstv.plugins import MethodPlugin

##################################################################

#  Meek STV per New Zealand rules
#
#  Clauses handled in STV.py:
#    7 (initial keep factor): OK
#        RecursiveSTV.initializeTreeAndKeepFactors() sets all to 1,
#        which will be correct when winners are determined
#    17 (updated keep factors): OK: RecursiveSTV.updateKeepFactors()
#    10 (allocate votes): OK?
#        MeekSTV.treeCount(): result is always exact(?)
#    11 (quota): OK: STV.updateThresh()
#    13 (threshold of exclusion): via surplusLimit
#
#  A cautionary note:
#    The New Zealand "STV Calculator", which does the actual counting,
#    does not conform to the published specification linked below
#    (Schedule 1A). This implementation attempts to follow the STV
#    Calculator where it differs from Schedule 1A; however, without
#    access to the Calculator, it's impossible to guarantee that it
#    matches in all respects.
#
class MeekNZSTV(MeekSTV, MethodPlugin):
  "MeekNZ STV"

  methodName = "MeekNZ STV"
  longMethodName = "New Zealand Meek STV"
  status = 2

  htmlBody = """
<p>This variation on Meek STV conforms to the New Zealand method as described here:
http://www.legislation.govt.nz/regulation/public/2001/0145/latest/DLM57125.html.
In particular, it uses nine digits of precision and employs its own random
number generator for breaking ties.</p>
<p>This method has not been verified, and may not be fully compliant with the New Zealand rules.</p>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    # Note: we're deliberate bypassing MeekSTV.__init__ here
    # because we don't want any UI options
    RecursiveSTV.__init__(self, b)
    MethodPlugin.__init__(self)
    self.weakTieBreakMethod = "forward" # per clauses 19, 34 & 40
    self.prec = 9                       # per clause 5
    self.prng_cands = {}

  class NZprng(object):
    "NZ PRNG per clauses 40-48"

    def __init__(self, c=None, n=None, v=None):
      "initialize PRNG per clause 42"
      self.x = c + 5
      self.y = n
      # 10000 per David Hill; clause 42 has 1000
      self.z = (v+10000*(v % 10)) % 30323
      # prime PRNG per clause 44
      self.next()
      self.next()
      self.next()
      self.next()

    def next(self):
      "generate next random number per clause 43"
      self.x = (171*self.x) % 30269
      self.y = (172*self.y) % 30307
      self.z = (170*self.z) % 30323
      # the final mod 10000 per David Hill (clause 43 omits this)
      rc = ((10000*self.x)//30269 + (10000*self.y)//30307 + (10000*self.z)//30323) % 10000
      # start with an inversion per David Hill (clause 48 seens to suggest otherwise)
      rc = 10000 - rc
      return rc

  def preCount(self):
    "MeekNZ STV: prepare for count"
    MeekSTV.preCount(self)
    self.strongTieBreakMethod = "random" # documentation only; we override breakStrongTie()

    self.surplusLimit = self.p / 10000	# 0.0001 per clause 13
    # initialize PRNG per clause 42
    prng = MeekNZSTV.NZprng(c=self.b.numCandidates, n=self.numSeats, v=self.b.numBallots)
    for c in self.continuing:
      rc = prng.next()
      while rc in self.prng_cands.values():
        rc = prng.next()
      self.prng_cands[c] = rc

  #  NOTE
  #  This is a variation on MeekSTV.treeCount that rounds up
  #  keep factors per NZ clause 10
  #
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
      #
      #  allocate votes for this ballot
      #
      #  provisional: three methods for comparison
      #
      method = "hill"
      if method == "hill":
        # this appears to produce results consistent with David Hill's implementation
        # and (presumably) the NZ STV Calculator
        keep, rem = divmod(rrr * self.keepFactor[self.R][c], self.p)
        if rem > 0:
          keep += 1   # round up per clause 10
        self.count[self.R][c] += keep * tree[c]["n"]  # times ballot count
        rrr -= keep
      elif method == "nz":
        # this is the method according to NZ Schedule 1A clause 10
        keep, rem = divmod(rrr * self.keepFactor[self.R][c], self.p)
        if rem > 0:
          keep += 1   # round up per clause 10
        self.count[self.R][c] += keep * tree[c]["n"]  # times ballot count
        rrr, rem = divmod(rrr * (1 - self.keepFactor[self.R][c]), self.p)
        if rem > 0:
          rrr += 1    # round up per clause 10
      else:
        # this is the method used by MeekSTV.py
        self.count[self.R][c] += rrr * self.keepFactor[self.R][c] * tree[c]["n"] / self.p
        rrr = rrr * (self.p - self.keepFactor[self.R][c]) / self.p
      # If ballot not used up, keep going
      if rrr > 0:
        self.updateCount(tree[c], rrr)

  def inInfiniteLoop(self):
    "Detect hangs by looking for at keep factor changes"
    if MeekSTV.inInfiniteLoop(self):
      return True
    if (self.R > 1):
      for kf1, kf2 in zip(self.keepFactor[self.R-2], self.keepFactor[self.R-1]):
        if kf2 > kf1:  # if any keep factor increased, we're in a loop
          return True
    return False

  def getSureLoser(self, ctng):
    "Return one sure loser (if one exists)."

    R = self.R - 1
    ctng.sort(key=lambda a, f=self.count[R]: f[a])

    if len(ctng) + len(self.winners) > self.numSeats:
      if (self.count[R][ctng[0]] + self.surplus[R]) < self.count[R][ctng[1]]:
        return ctng[0:1]
    return []

  def selectCandidatesToEliminate(self):
    "Eliminate losing candidates."

    # The NZ STV Calculator does multiple eliminations, though Schedule 1A does not.
    #
    # If total surplus < 0.00001, eliminate all candidates with zero votes.
    # Then perform normal elimination of one more loser.

    desc = ""

    #  If surplus is below limit, eliminate all candidates with zero votes
    losers = []
    ctng = list(self.continuing)
    if self.surplus[self.R-1] < self.surplusLimit:
      for c in self.continuing:
        if (self.count[self.R-1][c] == 0):
          losers.append(c)
          ctng.remove(c)
    # Eliminate one sure loser regardless of surplus limit
    if losers == []:
      losers = self.getSureLoser(ctng)

    #  If no other losers and surplus less than limit, find lowest candidate
    if losers == [] and self.surplus[self.R-1] < self.surplusLimit:
      (c, desc) = self.breakWeakTie(self.R-1, ctng, "fewest",
                                    "candidates to eliminate")
      losers = [c]

    # Special case to prevent infinite loops caused by fixed precision
    # This is different from the Hill stable-state logic, but consistent with the
    # rather vague Schedule 1A clause 23 language.
    if losers == [] and self.inInfiniteLoop():
      desc = "Candidates tied within precision of computations. "
      (c, desc2) = self.breakWeakTie(self.R-1, self.continuing, "fewest",
                                     "candidates to eliminate")
      losers = [c]
      desc += desc2

    self.newLosers(losers)

    return losers, desc

  def eliminateCandidates(self):
    "Find candidate(s) to eliminate and transfer their votes"
    (losers, descChoose) = self.selectCandidatesToEliminate()
    if losers != []:
      self.roundInfo[self.R]["action"] = ("eliminate", losers)
      descTrans = self.transferVotesFromCandidates(losers)
      self.roundInfo[self.R]["eliminate"] = descTrans + descChoose

  def breakStrongTie(self, tiedC, what=""):
    "Break strong tie between candidates using Meek NZ PRNG per clauses 19 & 34"

    assert(len(tiedC) >= 1)

    # If we have the right number, then return all.
    if len(tiedC) == 1:
      return (tiedC[0], None)

    # Sort all the candidates by PRN and then return the first tied candidate from the resulting list
    # Note that round number R starts at 1, and we reverse on even rounds
    for c in sorted(self.prng_cands.keys(), key=lambda k: self.prng_cands[k], reverse=(self.R & 1)==0):
      if c in tiedC:
        desc = "Candidate %s was chosen by breaking the tie randomly. " % \
              self.b.names[c]
        return (c, desc)
    raise RuntimeError, "Internal error breaking strong tie."

  #  Differs from MeekSTV in that it rounds up the intermediate
  #  keep factor calculation.
  #
  def updateKeepFactors(self):
    "Udpate the candidate keep factors."

    if len(self.winners) != 0:
      desc = "Keep factors of candidates who have exceeded the threshold: "
      winners = []
    else:
      desc = ""

    candidateList = list(self.continuing | self.winners)
    candidateList.sort()
    for c in candidateList:
      if self.count[self.R-1][c] > self.thresh[self.R-1]:
        # for testing, support both NZ and OpenSTV rounding
        method = "nz"
        if method == "nz":
          kf, rem = divmod(self.keepFactor[self.R-1][c] * self.thresh[self.R-1], self.p)
          if rem > 0:
            kf += 1
          kf, rem = divmod(kf * self.p, self.count[self.R-1][c])
          if rem > 0:
            kf += 1
        else:
          kf, rem = divmod(self.keepFactor[self.R-1][c] * self.thresh[self.R-1],
                        self.count[self.R-1][c])
          if rem > 0:
            kf += 1
        self.keepFactor[self.R][c] = kf
        winners.append("%s, %s" % (self.b.names[c],
                                  self.displayValue(self.keepFactor[self.R][c])))
      else:
        self.keepFactor[self.R][c] = self.keepFactor[self.R-1][c]

    if len(self.winners) != 0:
      desc += self.b.joinList(winners, convert="none") + ". "
    return desc

  def describeRound(self):
    "Update message for this round"
    if self.roundInfo[self.R]["action"][0] == "first":
      text = "Count of first choices. "
    elif self.roundInfo[self.R].has_key("surplus") and \
         self.roundInfo[self.R].has_key("eliminate"):
      text = self.roundInfo[self.R]["eliminate"] + \
           self.roundInfo[self.R]["surplus"]
    elif self.roundInfo[self.R].has_key("surplus"):
      text = self.roundInfo[self.R]["surplus"]
    elif self.roundInfo[self.R].has_key("eliminate"):
      text = self.roundInfo[self.R]["eliminate"]

    if self.roundInfo[self.R].has_key("winners"):
      text += self.roundInfo[self.R]["winners"]

    self.msg[self.R] = text

  def countBallots(self):
    "Count the ballots using NZ Meek STV."

    # Count first place votes
    self.allocateRound()
    self.initialVoteTally()
    self.updateRound()
    self.describeRound()

    while (not self.electionOver()):
      self.R += 1
      self.allocateRound()
      self.eliminateCandidates()
      self.transferSurplusVotes()
      self.updateRound()
      self.describeRound()

    self.updateCandidateStatus()
