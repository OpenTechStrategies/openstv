"""Module that provides code that can be used for different counting methods.

Class ElectionMethod
  Class NonIterative
  Class Iterative
    Class STV
      Class OrderDependentSTV
      Class OrderIndependentSTV
        Class NoSurplusSTV
        Class GregorySTV
        Class WeightedInclusiveSTV
        Class RecursiveSTV
"""

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

__revision__ = "$Id: STV.py 822 2010-11-21 05:25:43Z jeff.oneill $"

import random

##################################################################

class ElectionMethod(object):
  """Base class for all election methods.  This class provides code that can be
  used for many different methods and is not a complete election method.
  Subclasses of this class create categories of election methods, and futher
  subclasses will create actual election methods.
  
  Arguments:
  
  The only argument to the constructor is the Ballots object continaing the 
  votes to be counted.
  
  Class Attributes:
  
    methodName -- Shorter method name used internally.

    longMethodName -- Longer method name used in generating reports.

    onlySingleWinner -- Some methods can only be used to elect one person.

    iterative -- Methods are either iterative or are not.

    threshMethod -- Some methods have a threshold for election.
  
  Instance Attributes:
  
    b -- The Ballots object passed in the constructor.

    numSeats -- The number of seats to be filled.

    title -- A title for the election.

    date -- A date for the election.

    withdrawn -- A list of candidate numbers of withdrawn candidates.
  
    losers -- Index numbers of candidates who have been eliminated.
    
    winners -- Index numbers of winning candidates.
  
    continuing -- Index numbers of candidates who are not losers or winners.
  
    strongTieBreakMethod -- A strong tie is one that is broken externally to the
    count (contrast with weak ties in Iterative methods).  Allowable values are
    "random", "alpha", "index", and "manual".

    breakTieRequestQueue, breakTieResponseQueue -- These are used to manually 
    break ties from a GUI.  The counting is done in a thread, and when a tie
    needs to be broken, the counting thread puts a request on the request 
    queue.  The main (GUI) thread asks the user to break the tie and puts the
    result on the response queue.
  
    prec -- The number of digits of precision for certain methods (e.g., Meek,
    Gregory, and Weighted Inclusive).

    p -- A scale factor for doing fixed-point computations.  Set to 10**prec.
  
    guiOptions -- As election methods are plugins, this tells a GUI what options
    to present to the user and how to do it.

    optionsMsg -- Stores test describing options used in the method for 
    reporting purposes.
  
  """

  methodName = None
  longMethodName = None
  onlySingleWinner = False
  iterative = None
  threshMethod = None

  def __init__(self, b):

    # Get information from ballot file.  Copy some attributes into the 
    # elections instance since the user may change them.
    self.b = b
    self.numSeats = b.numSeats
    self.title = b.title
    self.date = b.date

    # Defaults for options
    self.strongTieBreakMethod = "random"
    self.breakTieRequestQueue = None   # overridden if manual tiebreaking
    self.breakTieResponseQueue = None  # overridden if manual tiebreaking
    self.prec = 0
    self.p = 1
    self.guiOptions = []
    self.optionsMsg = ""
    
    self.winners = set()
    self.losers = set()
    self.continuing = set(range(self.b.numCandidates))
    
  def runElection(self):
    self.preCount()
    self.countBallots()
    self.postCount()

  def preCount(self):

    assert(self.strongTieBreakMethod in 
           ["random", "alpha", "index", "manual"])
    
    self.p = 10**self.prec     # Scale factor for computations

    # Check for sufficient candidates and ballots
    self.checkMinRequirements()
    
  def countBallots(self):
    raise NotImplementedError

  def postCount(self):
    pass

  def displayValue(self, value):
    "Format a value with specified precision."

    if self.prec == 0: 
      return str(value)
    nfmt = "%d.%0" + str(self.prec) + "d" # %d.%0_d
    return nfmt % (value/self.p, value%self.p)

  def checkMinRequirements(self):
    "Only attempt to count votes if there are enough candidates and voters."
    
    # some basic minimum requirements
    if self.b.numCandidates < 2:
      raise RuntimeError, """\
Not enough candidates to run an election.
Need at least %d candidates but have only %d.""" % (
        max(2, self.numSeats+1), self.b.numCandidates)

    if self.numSeats < 1:
      raise RuntimeError, "The number of seats must be at least 1."

  def findTiedCand(self, candidateList, mostfewest, values):
    """Return a list of candidates tied for first or last.
    
    candidateList is the list of candidates to be considered.
    
    mostfewest is "most" of "fewest" and indicates whether we are looking for
    candidates tied for first or last.
    
    values is the metric to be used for comparing candidates.  Often it will be
    self.count[r], but it could be anything.
    """

    assert(mostfewest in ["most", "fewest"])
    assert(len(candidateList) > 0)
    
    getMin = (mostfewest == "fewest") 
    candidateListValues = [values[c] for c in candidateList]
    if getMin:
      maxMinValue = min(candidateListValues)
    else:
      maxMinValue = max(candidateListValues)
    
    return [c for c in candidateList if values[c] == maxMinValue]

  def chooseNfromM(self, N, values, candidateList, what):
    "Choose the N candidates with the most votes."
    
    desc = ""
    if len(candidateList) <= N:
      return (candidateList, desc)

    chosen = []          # Candidates who will be chosen
    maybe = list(candidateList)     # Candidates who may be chosen
    maybe.sort(key=lambda a, f=values: -f[a])
    LC = maybe[N]        # First losing candidate
    cutoff = values[LC]

    # All candidates with more than the Nth are chosen
    for c in maybe[:]:
      if values[c] > cutoff:
        maybe.remove(c)
        chosen.append(c)
      elif values[c] < cutoff:
        maybe.remove(c)

    # Break a possible tie for Nth place
    if len(chosen) < N:
      maybe.sort()
      desc = "Candidates %s were tied when when choosing %s. "\
           % (self.b.joinList(maybe), what)
    while len(chosen) < N:
      (c, desc2) = self.breakStrongTie(maybe)
      desc += desc2
      chosen.append(c)
      maybe.remove(c)

    return (chosen, desc)

  def breakStrongTie(self, tiedCandidates, what=""):
    "Break a strong tie between candidates."

    assert(len(tiedCandidates) >= 1)
    
    # If we have the right number, then return all.
    if len(tiedCandidates) == 1:
      return (tiedCandidates[0], None)
    
    # Break the tie randomly.
    elif self.strongTieBreakMethod == "random":
      c = random.choice(tiedCandidates)
      desc = "Candidate %s was chosen by breaking the tie randomly. "\
           % self.b.names[c]

    # Break the tie alphabetically by candidate's names.
    elif self.strongTieBreakMethod == "alpha":
      tiedCandidates.sort(key=lambda a: self.b.names[a])
      c = tiedCandidates[0]
      desc = "Candidate %s was chosen by breaking the tie alphabetically. "\
           % self.b.names[c]

    # Break the tie by candidate index number.
    elif self.strongTieBreakMethod == "index":
      tiedCandidates.sort()
      c = tiedCandidates[0]
      desc = "Candidate %s was chosen by breaking the tie by candidate index "\
            "number. " % self.b.names[c]
      
    elif self.strongTieBreakMethod == "manual":
      self.breakTieRequestQueue.put(
        [tiedCandidates, [self.b.names[c] for c in tiedCandidates], what])
      c = self.breakTieResponseQueue.get(True)
      if c == None:
        c = random.choice(tiedCandidates)
        desc = "Candidate %s was chosen by breaking the tie randomly. "\
             % self.b.names[c]
      else:
        desc = "Candidate %s was chosen by breaking the tie manually. "\
             % self.b.names[c]

    else:
      assert(0)

    return (c, desc)

##################################################################

class NonIterative(ElectionMethod):
  """Class that provides additional functionality for noniterative methods.

  Attributes:
  
    count -- List containing the number of votes received by each candidate.
  
    exhausted -- Number of exhausted votes.

    msg -- String describing the count.
  
  """

  iterative = False

  def __init__(self, b):
    ElectionMethod.__init__(self, b)
    self.exhausted = 0
    self.msg = ""
    self.count = []

  def preCount(self):
    ElectionMethod.preCount(self)
    self.count = [0] * self.b.numCandidates

  def chooseWinners(self):
    "Choose the candidates with the most votes as the winners"
    
    for c in list(self.continuing):
      if self.count[c] == 0:
        self.continuing.remove(c)
        self.losers.add(c)
    
    (winners, desc) = self.chooseNfromM(self.numSeats, self.count,
                                        self.continuing, "winner")
    self.winners = set(winners)
    self.losers |= self.continuing - self.winners
    self.continuing = set()
    return desc

##################################################################

class Iterative(ElectionMethod):
  """Class that provides additional funcationilty for iterative methods.

  Attributes:
  
    count -- Contains the vote counts for candidates for each round.  
    count[r][c] stores candidate c's vote count at round r.
  
    exhausted -- A list of exhausted votes at each round.
  
    msg -- A list containing strings describing each round of the count.
  
    weakTieBreakMethod -- Method to break a tie at a given round.  Allowable
    values are "backward" (use the previous round), "forward" (use the first 
    round), "strong" (don't use other rounds to break tie).

    stopCond -- List containing one or more criteria for ending the election.  
    Allowable values are "Know Winners" (all the winners have been determined), 
    "N+1" (only N+1 candidates remain), "N" (only N candidates remain), and 
    "Continuing Empty" (all candidates are either winners or losers).

    R -- The number of the current round.

    numRounds -- The total number of rounds.
  
    winnersOver, winnersEven -- The union of these two is always the same as
    "winners".  A winning candidate is first placed in winnersOver.  After
    surplus votes have been transferred from a winning candidate he or she is
    moved from winners over to winners even.

    roundInfo -- Stores information about what happened during each round.
    roundInfo[r] is a dictionary that stores information about round r.
    Possible values include
        roundInfo[r]["action"] = ("first", [])
        roundInfo[r]["action"] = ("surplus", [list of candidates])
        roundInfo[r]["action"] = ("eliminate", [list of candidates])
        roundInfo[r]["winners"] = "Text describing winners"
        roundInfo[r]["surplus"] = "Text describing surplus transfer"
        roundInfo[r]["eliminate"] = "Text describing candidate elimination"
  
  """
  
  iterative = True
  threshMethod = True # methods may override this

  def __init__(self, b):
    ElectionMethod.__init__(self, b)

    self.weakTieBreakMethod = "backward"
    self.stopCond = None
    self.R = 0           # current round
    self.numRounds = 0
    self.msg = []            # msg[r] contains text describing round r
    self.count = []          # count[r][c] is candidate c's votes at round r
    self.exhausted = []      # exhausted[r] is number of exhausted votes

    self.roundInfo = []

    self.winnersEven = set() # winners who have had their surplus transferred
    self.winnersOver = set() # winners who still have a surplus
    self.wonAtRound = [None] * self.b.numCandidates
    self.lostAtRound = [None] * self.b.numCandidates
    
  def postCount(self):
    ElectionMethod.postCount(self)
    self.numRounds = self.R+1
  
  def allocateRound(self):  
    self.msg.append("")
    self.roundInfo.append({})
    self.count.append([0] * self.b.numCandidates)
    self.exhausted.append(0)

  def breakWeakTie(self, R, candidateList, mostfewest, what=""):
    """Break ties using previous rounds.

    A weak tie is a tie at a given round, and may be able to be broken by
    looking at other rounds.  A strong tie occurs when candidates are tied at
    all rounds.  Weak ties can be broken in three ways:
        forward -- start at round 1 and go forward
        backward -- start at the previous round and go backward
        strong -- don't use other rounds to break the tie
    """

    assert(mostfewest in ["most", "fewest"])
    tiedCandidates = self.findTiedCand(candidateList, mostfewest, self.count[R])
    if len(tiedCandidates) == 1:
      return (tiedCandidates[0], "") # no tie

    # Let the user know what is going on.
    tiedCandidates.sort()
    desc = "Candidates %s were tied when choosing %s. "\
           % (self.b.joinList(tiedCandidates), what)
    
    # When method is "strong", we go straight to strong tie breaking.
    if self.weakTieBreakMethod == "strong":
      (c, desc2) = self.breakStrongTie(tiedCandidates, what)
      return c, desc + desc2

    # When method is "forward" or "backward" we use other rounds
    order = range(R)
    if self.weakTieBreakMethod == "backward":
      order.reverse()
    
    if self.weakTieBreakMethod in ["forward", "backward"]:
      for i in order:
        tiedCandidates = self.findTiedCand(tiedCandidates, mostfewest, self.count[i])
        if len(tiedCandidates) == 1:
          desc += "Candidate %s was chosen by breaking the tie at round %d. "\
                  % (self.b.names[tiedCandidates[0]], i+1)
          return (tiedCandidates[0], desc)

    # The tie can't be broken with other rounds so do strong tie break.
    (c, desc2) = self.breakStrongTie(tiedCandidates, what)
    return c, desc + desc2

  def newWinners(self, newWinnersList, status="over"):
    "Perform basic accounting when a new winner is found."

    assert(len(newWinnersList) > 0)
    
    newWinnersList.sort()
    for c in newWinnersList:
      assert(self.count[self.R][c] > 0)
      self.continuing.remove(c)
      self.winnersOver.add(c)
      self.wonAtRound[c] = self.R
    self.winners = self.winnersOver | self.winnersEven
    
    if len(newWinnersList) == 1 and status == "over":
      desc = "Candidate %s has reached the threshold and is elected. "\
             % self.b.joinList(newWinnersList)
    elif len(newWinnersList) == 1 and status == "under":
      desc = "Candidate %s is elected. " % self.b.joinList(newWinnersList)
    elif status == "over":
      desc = "Candidates %s have reached the threshold and are elected. "\
             % self.b.joinList(newWinnersList)
    elif status == "under":
      desc = "Candidates %s are elected. " % self.b.joinList(newWinnersList)
    else:
      assert(0)

    return desc

  def newLosers(self, newLosersList):
    "Perform basic accounting when a new loser is found."
    
    assert(newLosersList > 0)
    for c in newLosersList:
      self.continuing.remove(c)
      self.losers.add(c)
      self.lostAtRound[c] = self.R

  def electionOver(self):
    "Determine whether the election is over."
    
    # Election is over when all winners have been identified
    if ("Know Winners" in self.stopCond and
        len(self.winners) == self.numSeats):
      return True
      
    # Election is over when N+1 or fewer candidates remain
    if ("N+1" in self.stopCond and
        len(self.continuing) + len(self.winners) <= self.numSeats + 1):
      return True

    # Election is over when fewer than N candidates remain
    if ("N" in self.stopCond and
        len(self.continuing) + len(self.winners) <= self.numSeats):
      return True
    
    # Election is over when no candidates left in continuing
    if "Continuing Empty" in self.stopCond and len(self.continuing) == 0:
      return True

    return False

##################################################################

class STV(Iterative):
  """Class that provides additional functionality for STV methods.
  
  Attributes:
  
    threshName -- The name of the winning threshold to use.  This is a tuple of
    three criteria.  The first is "Droop" or "Hare".  The second is "Static" or 
    "Dynamic".  The third is "Whole" or "Fractional".  
  
    delayedTransfer --  Some methods allow the transfer of surplus votes to be 
    delayed where candidates can be safely eliminate.  Allowable values are
    "On" and "Off".
  
    surplus -- A list containing the surplus votes at each round.
  
    thresh -- A list contiaining the winning threshold at each round.
  
    votes -- Contains the votes assigned to each candidate.  votes[c] is a list
    containing the index numbers of all votes assigned to candidate c.

    batchElimination -- Some methods allow multiple candidates to be eliminated
    in a single round.  Allowable values are "None" (no batch elimination), 
    "Zero" (all candidates with zero votes eliminated simultaneously), "Cutoff"
    (all candidates with fewer than a specified number of votes are eliminated
    simultaneously), "Losers" (all losing candidates eliminated simultaneously),
    and "LosersERS97" (similar to "Losers" but as defined in ERS97 rules).
  
    batchCutoff -- When batchElimination is "Cutoff", this is the cutoff.
  
    firstEliminationRound -- Initially set to true.  Set to false after the
    first elimination round.
  
  """

  def __init__(self, b):
    Iterative.__init__(self, b)
    self.stopCond = ["Know Winners", "N"]
    self.threshName = None  # must be overridden
    self.delayedTransfer = "Off"
    self.batchElimination = None       # must be overridden
    self.batchCutoff = None
    self.firstEliminationRound = True
    self.surplus = []    # surplus[r] is number of surplus votes
    self.thresh = []     # thresh[r] is the winning threshold
    # votes[c] stores the indices of all votes for candidate c.
    self.votes = []

  def preCount(self):
    Iterative.preCount(self)
    for _c in range(self.b.numCandidates):
      self.votes.append([])
 
  def allocateRound(self):
    "Allocate space for all data structures for one round."
    Iterative.allocateRound(self)
    self.surplus.append(0)
    self.thresh.append(0)

  def initialVoteTally(self):
    "Count the first place votes (must be overridden)."
    raise NotImplementedError
  
  def updateCount(self):
    raise NotImplementedError
  
  def updateExhaustedVotes(self):
    """Compute the number of exhausted votes"""
    exhausted = self.p * self.b.numBallots
    exhausted -= sum(self.count[self.R])
    self.exhausted[self.R] = exhausted

  def updateThresh(self):
    "Compute the value of the winning threshold."

    assert(self.threshName[0] in ["Droop", "Hare"])
    assert(self.threshName[1] in ["Static", "Dynamic"])
    assert(self.threshName[2] in ["Whole", "Fractional"])

    if self.threshName[0] == "Droop":
      threshDen = self.numSeats + 1
    elif self.threshName[0] == "Hare":
      threshDen = self.numSeats

    if self.threshName[1] == "Static":
      threshNum = self.p * self.b.numBallots
    elif self.threshName[1] == "Dynamic":
      threshNum = self.p * self.b.numBallots - self.exhausted[self.R]

    if self.threshName[2] == "Whole":
      thresh = threshNum/threshDen/self.p*self.p + self.p
    elif self.threshName[2] == "Fractional":
      thresh = threshNum/threshDen + 1

    self.thresh[self.R] = thresh
  

  def updateSurplus(self):
    "Compute the surplus for current round."

    self.surplus[self.R] = 0
    for c in self.winnersOver | self.continuing:
      if self.count[self.R][c] > self.thresh[self.R]:
        self.surplus[self.R] += self.count[self.R][c] - self.thresh[self.R]

  def updateWinners(self):
    "Find new winning candidates."

    winners = []
    for c in self.continuing:
      if self.count[self.R][c] >= self.thresh[self.R]:
        winners.append(c)

    if len(winners) > 0:
      text = self.newWinners(winners)
      # In some instances, updateWinners could be called more than once in a 
      # single round (e.g., N. Ireland STV when eliminating losers).
      if self.roundInfo[self.R].has_key("winners"):
        self.roundInfo[self.R]["winners"] += text
      else:
        self.roundInfo[self.R]["winners"] = text

  def updateRound(self):
    self.updateCount()
    self.updateExhaustedVotes()
    self.updateThresh()
    self.updateSurplus()
    self.updateWinners()
    
  def describeRound(self):
    
    if self.roundInfo[self.R]["action"][0] == "first":
      text = "Count of first choices. "
    elif self.roundInfo[self.R]["action"][0] == "surplus":
      text = self.roundInfo[self.R]["surplus"]
    elif self.roundInfo[self.R]["action"][0] == "eliminate":
      text = self.roundInfo[self.R]["eliminate"]
      
    if self.roundInfo[self.R].has_key("winners"):
      text += self.roundInfo[self.R]["winners"]
      
    # Explain what will happen in the next round
    if self.electionOver() or not self.threshMethod:
      pass
    elif self.surplus[self.R] == 0:
      text += "No candidates have surplus votes so candidates will be "\
           "eliminated and their votes transferred for the next round. "
    elif self.delayedTransfer == "On" and len(self.getSureLosers(self.R)) != 0:
      text += "Candidates have surplus votes, but since "\
           "candidates can be safely eliminated, the transfer of surplus "\
           "votes will be delayed and candidates will be eliminated and their "\
           "votes transferred for the next round."
    else:
      text += "Candidates have surplus votes so "\
           "surplus votes will be transferred for the next round. "

    self.msg[self.R] = text
    
  def isSurplusToTransfer(self):
    "Decide whether to transfer surplus votes or eliminate candidates."
    
    if ( self.surplus[self.R-1] == 0 or
         (self.delayedTransfer == "On" and len(self.getSureLosers()) != 0) ):
      return False
    else:
      return True
    
  def transferSurplusVotes(self):

    (c, selectSurplusDesc) = self.selectSurplusToTransfer()
    
    self.roundInfo[self.R]["action"] = ("surplus", [c])
    self.winnersOver.remove(c)
    self.winnersEven.add(c)
    
    transferSurplusDesc = self.transferSurplusVotesFromCandidate(c)
    
    self.roundInfo[self.R]["surplus"] = transferSurplusDesc
    self.roundInfo[self.R]["surplus"] += selectSurplusDesc

  def selectSurplusToTransfer(self):
    "Choose the candidate whose surplus will be transferred."

    # Choose the candidate with the greatest surplus.
    (c, desc) = self.breakWeakTie(self.R-1, list(self.winnersOver), "most",
                                  "surplus to transfer")
    return (c, desc)

  def transferSurplusVotesFromCandidate(self, c):
    "This must be overridden"
    raise NotImplementedError
  
  def getSureLosers(self, R=None):
    "Return all candidates who are sure losers."

    # Return all candidates who are sure losers but do not look at previous
    # rounds to break ties.

    if R is None: 
      R = self.R - 1
      
    maxNumLosers = len(self.continuing) + len(self.winners) - self.numSeats
    assert(maxNumLosers < len(self.continuing))
    losers = []

    # If all continuing candidates have zero votes and there is no surplus
    # then they are all sure losers.
    totalContinuingVote = sum([self.count[R][c] for c in self.continuing])
    if totalContinuingVote == 0 and self.surplus[R] == 0:
      losers = list(self.continuing)
      return losers
    
    # We need to make sure that all candidates with the same number of votes
    # are treated the same, so group candidates with the same number of votes
    # together and sort clusters in order of votes (fewest first).
    continuing = list(self.continuing)
    continuing.sort(key=lambda a, f=self.count[R]: f[a])
    clusteredContinuing = [[continuing[0]]]
    for c in continuing[1:]:
      if self.count[R][c] == self.count[R][ clusteredContinuing[-1][0] ]:
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
      
      if ((self.batchElimination != "LosersERS97" and s < nextClusterCount) or
          (self.batchElimination == "LosersERS97" and s <= nextClusterCount))\
         and len(potentialLosers) <= maxNumLosers:
        losers = potentialLosers[:]
        
    return losers

  def eliminateCandidates(self):
    (elimList, selectLosersDesc) = self.selectCandidatesToEliminate()
    self.roundInfo[self.R]["action"] = ("eliminate", elimList)
    transferVotesDesc = self.transferVotesFromCandidates(elimList)
    self.roundInfo[self.R]["eliminate"] = transferVotesDesc + selectLosersDesc

  def selectCandidatesToEliminate(self):
    "Choose one or more candidates to eliminate."

    elimList = []
      
    # First elimination round is different for some methods
    # Skipped if no candidates would be eliminated
    if self.firstEliminationRound:

      if self.batchElimination == "Zero":
        desc = "Since this is the first elimination round, all candidates "\
               "without any votes are eliminated. "
        elimList = [c for c in self.continuing if self.count[self.R-1][c] == 0]
      elif self.batchElimination == "Cutoff":
        desc = "Since this is the first elimination round, all candidates "\
               "with fewer than %d votes are eliminated. " % \
               self.batchCutoff
        elimList = [c for c in self.continuing
                    if self.count[self.R-1][c] < self.p*self.batchCutoff]
      elif self.batchElimination in ["Losers", "LosersERS97"]:
        desc = "All losing candidates are eliminated. "
        elimList = self.getSureLosers()
        # We can eliminate one more candidate if all of the following are 
        # satisfied:
        # (1) The surplus is zero
        # (2) The candidates selected for elimination all have zero votes
        # (3) There are enough candidates remaining
        if ( self.surplus[self.R-1] == 0):
          ctng = [c for c in self.continuing if c not in elimList]
          if ( len(ctng) + len(self.winners) > self.numSeats):
            elimListTotalCount = sum([self.count[self.R-1][c] for c in elimList])
            if ( elimListTotalCount == 0):
              (c, desc2) = self.breakWeakTie(self.R-1, ctng, "fewest",
                                             "candidates to eliminate")
              elimList.append(c)
              desc += desc2
      elif self.batchElimination == "None":
        pass
      else:
        assert(0)

    # Normal elimination round
    # This happens if not firstEliminationRound or if the first
    # elimination round didn't eliminate any candidates.
    if (not self.firstEliminationRound) or (len(elimList) == 0):
      if self.batchElimination in ["Losers", "LosersERS97"]:
        desc = "All losing candidates are eliminated. "
        elimList = self.getSureLosers()
        if len(elimList) == 0:
          (c, desc2) = self.breakWeakTie(self.R-1, list(self.continuing), "fewest",
                                        "candidates to eliminate")
          elimList = [c]
          desc += desc2
      else:
        (c, desc) = self.breakWeakTie(self.R-1, self.continuing, "fewest",
                                      "candidates to eliminate")
        elimList = [c]

    # Don't do first elimination again.
    self.firstEliminationRound = False

    # Put losing candidates in the proper list
    self.newLosers(elimList)

    return (elimList, desc)

  def transferVotesFromCandidates(self, elimList):
    raise NotImplementedError
  
  def updateCandidateStatus(self):
    "Update candidate status at end of election."

    desc = ""

    if len(self.winners) == self.numSeats:
      # All others are losers
      self.newLosers(list(self.continuing))

    else:
      # Candidates with no votes are losers
      for c in list(self.continuing):
        if self.count[self.R][c] == 0:
          self.newLosers([c])
      # Eliminate (N+1)th candidate
      if len(self.continuing) + len(self.winners) > self.numSeats:
        (c, desc) = self.breakWeakTie(self.R, self.continuing, "fewest",
                                      "winners")
        self.newLosers([c])
      # Everyone else is a winner
      if len(self.continuing) > 0:
        desc += self.newWinners(list(self.continuing), "under")
      
    self.msg[self.R] += desc

  def countBallots(self):
    "Count the votes with STV."

    # Count first place votes
    self.allocateRound()
    self.initialVoteTally()    
    self.updateRound()
    self.describeRound()
    
    # Transfer surplus votes or eliminate candidates until done
    while (not self.electionOver()):
      
      self.R += 1
      self.allocateRound()

      if self.isSurplusToTransfer():
        self.transferSurplusVotes()
      else:
        self.eliminateCandidates()

      self.updateRound()
      self.describeRound()

    self.updateCandidateStatus()

##################################################################

class OrderDependentSTV(STV):
  """Class that provides additionaly functionality for STV methods that are
  dependent of the order of the ballots.  Order dependent methods must use
  individual ballots and cannot use weighted ballots.
  
  No additional attributes.
  
  """

  def __init__(self, b):    
    STV.__init__(self, b)

  def preCount(self):
    STV.preCount(self)
    assert(self.threshName[2] == "Whole")
      
  def initialVoteTally(self):
    "Count the first place votes with order dependent rules."

    # Allocate votes to candidates bases on the first choices.
    for i in xrange(self.b.numBallots):
      c = self.b.getTopChoiceFromBallot(i, self.continuing)
      if c is not None: 
        self.votes[c].append(i)

    self.roundInfo[self.R]["action"] = ("first", [])
    
  def updateCount(self):
    "Update the vote totals after a transfer of votes."

    for c in range(self.b.numCandidates):
      self.count[self.R][c] = len(self.votes[c])

##################################################################

class OrderIndependentSTV(STV):
  """Class that provides additionaly functionality for STV methods that are
  independent of the order of the ballots.  Order independent methods can use
  weighted ballots to speed up the count.
  
  No additional attributes.
  
  """

  def initialVoteTally(self):
    "Count the first place votes."

    # Allocate votes to candidates based on the first choices.
    for i in range(self.b.numWeightedBallots):
      c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
      if c is not None: 
        self.votes[c].append(i)
    self.roundInfo[self.R]["action"] = ("first", [])

##################################################################

class NoSurplusSTV(OrderIndependentSTV):
  """Class that provides additionaly functionality for STV methods that do not
  have a winning threshold and thus do not have surplus votes.
  
  No additional attributes.
  
  """

  threshMethod = False

  def __init__(self, b):
    OrderIndependentSTV.__init__(self, b)
    self.threshName = None
    self.stopCond = ["N+1"]

  def updateThresh(self):
    "These methods don't have a threshold."
    pass
  
  def updateSurplus(self):
    "These methods don't have surplus votes."
    pass
    
  def isSurplusToTransfer(self):
    "Never transfer surplus votes."
    return False
  
  def transferVotesFromCandidates(self, elimList):
    "Eliminate candidates for NoSurplus methods."

    for loser in elimList:
      for i in self.votes[loser]:
        c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
        if c is not None:
          self.votes[c].append(i)
      self.votes[loser] = []

    desc = "Count after eliminating %s and transferring votes. " \
         % self.b.joinList(elimList)
    return desc
  
  def updateWinners(self):
    "Since there is no threshold, winners are only determined at the end."
    pass
    
  def updateCount(self):
    "Update the vote totals after a transfer of votes for NoSurplus methods."

    # Recount votes for all candidates
    for c in range(self.b.numCandidates):
      for i in self.votes[c]:
        self.count[self.R][c] += self.b.getWeight(i)

##################################################################

class GregorySTV(OrderIndependentSTV):
  """Class that provides additional functionality for Gregory STV methods.  
  Note that some of the quirks of the ERS97 STV rules are addressed in this
  classs to allow for more code reuse.
  
  Attributes:
  
    quota -- The quota for the ERS97 rules.
  
    S -- The current "stage" for ERS97 rules.  In transferring votes from
    eliminated candidates, the ERS97 rules use "substages".  Each substage is a 
    round so the number of rounds is greater than the number of stages.

    stages -- This is used to translate between rounds and stages.  stages[s] is
    a list of the rounds corresponding to that stage.

    votesByTransferValue -- In eliminating candidates, Gregory methods transfer
    votes in packets having the same transfer value.  votesByTransferValue[v]
    is a list of vote indices having that transfer value.
  
    batches -- In doing secondary transfers, Gregory methods transfer the last
    batch of votes received by a candidate.  batches[c] is a list of batches
    of votes received by candidate c.  Each batch is a list of vote indices.
  
    transferValue -- Each ballot has a transfer value.  Initially, it is set 
    to 1, but may be reduced when a vote is part of a surplus transfer.
  
  """
  
  def __init__(self, b):
    OrderIndependentSTV.__init__(self, b)
    self.quota = 0
    self.S = 0
    self.stages = []
    self.votesByTransferValue = []
    # Gregory rules do last batch transfers
    # Need to store batches for each cand
    self.batches = []
    self.transferValue = []
    self.transferValues = []

  def preCount(self):
    OrderIndependentSTV.preCount(self)
    
    self.transferValue = [self.p] * self.b.numWeightedBallots
    for _c in range(self.b.numCandidates):
      self.batches.append([])
  
  def initialVoteTally(self):
    "Count the first place votes with Gregory rules."

    OrderIndependentSTV.initialVoteTally(self)
    
    # The first batch is all the votes a candidate has.
    for c in range(self.b.numCandidates):
      self.batches[c].append(self.votes[c][:])

  def transferSurplusVotesFromCandidate(self, cSurplus):
    "Transfer surplus votes according to the Gregory rules."

    # Each candidate will receive a new batch of votes so
    # create a data structure to store the vote indices.
    newBatch = []
    for c in range(self.b.numCandidates):
      newBatch.append([])

    # We need to compute several quantities:
    #   surplus -- the number of votes of the transferor over quota
    #   transferableValue -- total value of batch to be transferred
    if self.methodName == "ERS97 STV":
      surplus = self.count[self.R-1][cSurplus] - self.quota[self.R-1]
    elif self.methodName == "N. Ireland STV":
      surplus = self.count[self.R-1][cSurplus] - self.thresh[self.R-1]
    lastBatch = self.batches[cSurplus][-1]
    transferableValue = 0
    nTransferable = 0
    for i in lastBatch:
      if self.b.getTopChoiceFromWeightedBallot(i, self.continuing) \
         is not None:
        transferableValue += \
                          self.b.getWeight(i) * self.transferValue[i]
        nTransferable += self.p * self.b.getWeight(i)

    # Do the transfer
    for i in lastBatch:
      if transferableValue > surplus:
        self.transferValue[i] = self.p * surplus / nTransferable
      c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
      if c is not None:
        self.votes[c].append(i)
        newBatch[c].append(i)

    # for candidates who received votes, add new batch
    for c in self.continuing:
      if len(newBatch[c]) > 0:
        self.batches[c].append(newBatch[c])

    self.votes[cSurplus] = []

    desc = "Count after transferring surplus votes from %s. " % \
         self.b.names[cSurplus]
    return desc

  def updateCount(self):
    "Update the vote totals after a transfer of votes."

    # Update counts for losers, continuing, and winnersOver.
    # Because of substage transfers with ERS97, losing candidates
    # will sometimes have a count greater than 0.
    for c in self.losers | self.continuing | self.winnersOver:
      self.count[self.R][c] = 0
      for i in self.votes[c]:
        self.count[self.R][c] += \
            self.b.getWeight(i) * self.transferValue[i]

    # Set counts for winnersEven.  This will always be the same as the
    # previous round.
    for c in self.winnersEven:
      self.count[self.R][c] = self.count[self.R-1][c]

    # Set counts for the candidate in transition from winnersOver to
    # winnersEven.  The transferor must be treated differently from
    # winnersOver and winnersEven.
    if self.roundInfo[self.R]["action"][0] == "surplus":
      cSurplus = self.roundInfo[self.R]["action"][1][0]
      if self.methodName == "N. Ireland STV":
        self.count[self.R][cSurplus] = self.thresh[self.R-1]
      elif self.methodName == "ERS97 STV":
        self.count[self.R][cSurplus] = self.quota[self.R-1]
      else:
        assert(0)

    
  def transferVotesWithValue(self, v):
    "Eliminate candidates according to the Gregory rules."

    # Set up holders for transferees
    newBatch = []
    for c in range(self.b.numCandidates):
      newBatch.append([])

    # Transfer votes of this value
    for i in self.votesByTransferValue[v]:
      c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
      if c is not None:
        self.votes[c].append(i)
        newBatch[c].append(i)
      # Don't know where this vote came from so try all losers
      for d in self.losers:
        if i in self.votes[d]:
          self.votes[d].remove(i)

    # For candidates who received votes, add new batch
    for c in self.continuing:
      if len(newBatch[c]) > 0:
        self.batches[c].append(newBatch[c])

  def eliminateCandidates(self):
    (elimList, selectLosersDesc) = self.selectCandidatesToEliminate()
    self.roundInfo[self.R]["action"] = ("eliminate", elimList)
    self.roundInfo[self.R]["eliminate"] = selectLosersDesc
    self.sortVotesByTransferValue(elimList)
    self.transferVotesFromCandidates(elimList)

  def sortVotesByTransferValue(self, elimList):
    raise NotImplementedError
  
  def countBallots(self):
    "Count the votes with Gregory rules."

    # Count first place votes
    self.allocateRound()
    if self.methodName == "ERS97 STV":
      self.stages.append([])
      self.stages[self.S].append(self.R)
    self.initialVoteTally()    
    self.updateRound()
    self.describeRound()
    
    # Transfer surplus votes or eliminate candidates until done
    while (not self.electionOver()):
      
      self.R += 1
      self.allocateRound()
      if self.methodName == "ERS97 STV":
        self.S += 1
        self.stages.append([])
        self.stages[self.S].append(self.R)

      if self.isSurplusToTransfer():
        self.transferSurplusVotes()
        self.updateRound()
        self.describeRound()
      else:
        self.eliminateCandidates()

    self.updateCandidateStatus()

##################################################################

class WeightedInclusiveSTV(OrderIndependentSTV):
  """Class that provides additional functionality for weighted inclusive 
  methods.
  
  Attributes:
  
    transferValue -- Each ballot has a transfer value.  Initially, it is set 
    to 1, but may be reduced when a vote is part of a surplus transfer.

  """

  def __init__(self, b):    
    OrderIndependentSTV.__init__(self, b)
    self.transferValue = []

  def preCount(self):
    OrderIndependentSTV.preCount(self)
    self.transferValue = [self.p] * self.b.numWeightedBallots
    
  def transferSurplusVotesFromCandidate(self, cSurplus):
    "Transfer the surplus votes of one candidate."

    # Transfer all of the votes at a fraction of their value
    surplus = self.count[self.R-1][cSurplus] - self.thresh[self.R-1]
    for i in self.votes[cSurplus][:]:
      self.transferValue[i] = self.transferValue[i] * surplus / \
          self.count[self.R-1][cSurplus]
      c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
      if c is not None:
        self.votes[c].append(i)

    self.votes[cSurplus] = []
    
    desc = "Count after transferring surplus votes from %s with a transfer "\
         "value of %s/%s. " \
         % (self.b.names[cSurplus], self.displayValue(surplus),
            self.displayValue(self.count[self.R-1][cSurplus]))
    return desc

  def updateCount(self):
    "Update the vote totals after a transfer of votes."

    # Update counts for losers, continuing, and winnersOver.
    for c in self.losers | self.continuing | self.winnersOver:
      self.count[self.R][c] = 0
      for i in self.votes[c]:
        self.count[self.R][c] += \
            self.b.getWeight(i) * self.transferValue[i]

    # Set counts for winnersEven.  This will always be the same as the
    # previous round.
    for c in self.winnersEven:
      self.count[self.R][c] = self.count[self.R-1][c]

    # Set counts for the candidate in transition from winnersOver to
    # winnersEven.  The transferor must be treated differently from
    # winnersOver and winnersEven.
    if self.roundInfo[self.R]["action"][0] == "surplus":
      cSurplus = self.roundInfo[self.R]["action"][1][0]
      self.count[self.R][cSurplus] = self.thresh[self.R-1]
      
  def transferVotesFromCandidates(self, elimList):
    "Eliminate a list of candidates."

    # Transfer votes from losers simultaneously.
    for loser in elimList:
      for i in self.votes[loser]:
        c = self.b.getTopChoiceFromWeightedBallot(i, self.continuing)
        if c is not None:
          self.votes[c].append(i)
      self.votes[loser] = []

    elimList.sort()
    desc = "Count after eliminating %s and transferring votes. " \
         % self.b.joinList(elimList)
    return desc

##################################################################

class RecursiveSTV(OrderIndependentSTV):
  """Class that provides additional functionality for recursive STV methods.
  
  Attributes:
  
    keepFactor -- Each candidate is assigned a keep factor that is initially
    set to 1.  When a candidate's vote exceeds the winning threshold, the
    keep factor is reduced to transfer surplus votes to other candidates.
    
    tree -- A data structure that stores the votes in a tree and allows for
    faster algorithms.  The first level (below the root) contains the current 
    active first choices.  When a candidate has exceeded the winning threshold,
    then that node of the tree is expanded to another level.  When a candidate
    is eliminated, the tree is rebuilt to remove that canddiate entirely as if
    the candidate had never been in the election.
    
  """

  def __init__(self, b):
    OrderIndependentSTV.__init__(self, b)
    
    self.threshName = ["Droop", "Dynamic", "Fractional"]
    self.prec = 6
    self.surplusLimit = 1	# lsb, not 1.0
    self.delayedTransfer = "On"
    self.batchElimination = "Losers"
    self.keepFactor = []
    self.tree = {}

  def allocateRound(self):
    "Add keep factor allocation."
    OrderIndependentSTV.allocateRound(self)
    self.keepFactor.append([0] * self.b.numCandidates)
    
  def describeRound(self):
    
    if self.roundInfo[self.R]["action"][0] == "first":
      text = "Count of first choices. "
    elif self.roundInfo[self.R]["action"][0] == "surplus":
      text = self.roundInfo[self.R]["surplus"]
    elif self.roundInfo[self.R]["action"][0] == "eliminate":
      text = self.roundInfo[self.R]["eliminate"]
      
    if self.roundInfo[self.R].has_key("winners"):
      text += self.roundInfo[self.R]["winners"]
      
    self.msg[self.R] = text

  def initialVoteTally(self):
    "Initialize the tree data structure and candidate keep factors."

    # The tree stores exactly the ballot information needed to count the
    # votes.  The first level of the tree is the top active candidate
    # (winner or in continuing).  Since for winning candidates, a portion
    # of the ballot goes to the next candidate, the tree is extended until
    # it reaches a candidate in continuing or the ballot is exhausted.

    # In the beginning, all candidates are in continuing so there is only
    # one level in the tree.

    self.roundInfo[self.R]["action"] = ("first", [])

    for c in range(self.b.numCandidates):
      self.keepFactor[0][c] = self.p

    for i in xrange(self.b.numWeightedBallots):
      self.addBallotToTree(self.tree, i)

  def addBallotToTree(self, tree, ballotIndex, ballot=""):
    """Add one ballot to the tree.
    
    The root of the tree is a dictionary that has as keys the indicies of all 
    continuing and winning candidates.  For each candidate, the value is also
    a dictionary, and the keys of that dictionary include "n" and "bi".
    tree[c]["n"] is the number of ballots that rank candidate c first.
    tree[c]["bi"] is a list of ballot indices where the ballots rank c first.
    
    If candidate c is a winning candidate, then that portion of the tree is
    expanded to indicate the breakdown of the subsequently ranked candidates.
    In this situation, additional keys are added to the tree[c] dictionary
    corresponding to subsequently ranked candidates.
    tree[c]["n"] is the number of ballots that rank candidate c first.
    tree[c]["bi"] is a list of ballot indices where the ballots rank c first.
    tree[c][d]["n"] is the number of ballots that rank c first and d second.
    tree[c][d]["bi"] is a list of the corresponding ballot indices.
    
    Where the second ranked candidates is also a winner, then the tree is 
    expanded to the next level.  
    
    Losing candidates are ignored and treated as if they do not appear on the 
    ballots.  For example, tree[c][d]["n"] is the total number of ballots
    where candidate c is the first non-losing candidate, c is a winner, and
    d is the next non-losing candidate.  This will include the following
    ballots, where x represents a losing candidate:
    [c d]
    [x c d]
    [c x d]
    [x c x x d]
    
    During the count, the tree is dynamically updated as candidates change
    their status.  The parameter "tree" to this method may be the root of the
    tree or may be a sub-tree.
    """

    if ballot == "":
      # Add the complete ballot to the tree
      weight, ballot = self.b.getWeightedBallot(ballotIndex)
    else:
      # When ballot is not "", we are adding a truncated ballot to the tree,
      # because a higher-ranked candidate is a winner.
      weight = self.b.getWeight(ballotIndex)
    
    # Get the top choice among candidates still in the running
    # Note that we can't use Ballots.getTopChoiceFromWeightedBallot since
    # we are looking for the top choice over a truncated ballot.
    for c in ballot:
      if c in self.continuing | self.winners:
        break # c is the top choice so stop
    else:
      c = None # no candidates left on this ballot

    if c is None:
      # This will happen if the ballot contains only winning and losing
      # candidates.  The ballot index will not need to be transferred
      # again so it can be thrown away.
      return

    # Create space if necessary.
    if not tree.has_key(c):
      tree[c] = {}
      tree[c]["n"] = 0
      tree[c]["bi"] = []

    tree[c]["n"] += weight

    if c in self.winners:
      # Because candidate is a winner, a portion of the ballot goes to
      # the next candidate.  Pass on a truncated ballot so that the same
      # candidate doesn't get counted twice.
      i = ballot.index(c)
      ballot2 = ballot[i+1:]
      self.addBallotToTree(tree[c], ballotIndex, ballot2)
    else:
      # Candidate is in continuing so we stop here.
      tree[c]["bi"].append(ballotIndex)
      
  def updateTree(self, tree, loserSet):    
    "Update the tree data structure to account for new winners and losers."
    self.updateLoserTree(tree, loserSet)
    self.updateWinnerTree(tree, loserSet)

  def updateLoserTree(self, tree, loserSet):
    "Update the tree data structure to account for new losers."
    for c in loserSet.intersection(tree):
      for i in tree[c]["bi"]:
        ballot = self.b.getWeightedBallot(i)[1] # drop weight
        j = ballot.index(c)
        ballot2 = ballot[j+1:]
        self.addBallotToTree(tree, i, ballot2)
      del tree[c]

  def updateWinnerTree(self, tree, loserSet):
    "Update the tree data structure to account for new winners."
    for c in self.winners.intersection(tree):
      if len(tree[c]["bi"]) > 0:
        # The current candidate is a new winner (has ballot indices), so
        # expand this node to the next level.  There is no need to call
        # updateTree() recursively since addBallotToTree() will appropriately
        # expand lower nodes.
        for i in tree[c]["bi"]:
          ballot = self.b.getWeightedBallot(i)[1]
          j = ballot.index(c)
          ballot2 = ballot[j+1:]
          self.addBallotToTree(tree[c], i, ballot2)
        tree[c]["bi"] = []
      else:
        # The current candidate is an old winner, so recurse to see if
        # anything needs to be done at lower levels.
        self.updateTree(tree[c], loserSet)

  def inInfiniteLoop(self):
    "detect stable state as infinite loop"
    return self.R > 1 and self.keepFactor[self.R-1] == self.keepFactor[self.R-2]

  def isSurplusToTransfer(self):

    # We eliminate candidates if (1) there are losers, (2) the surplus is
    # below the surplus limit, or (3) we are stuck in an infinite loop.
    if self.surplus[self.R-1] < self.surplusLimit or \
       (self.delayedTransfer == "On" and len(self.getSureLosers()) != 0) or \
       self.inInfiniteLoop():
      return False
    else:
      return True
  
  def transferSurplusVotes(self):
    self.roundInfo[self.R]["action"] = ("surplus", [])
    self.updateTree(self.tree, self.losers)
    desc = self.updateKeepFactors()
    self.roundInfo[self.R]["surplus"] = \
        "Count after transferring surplus votes. " + desc
    
  def eliminateCandidates(self):
    (elimList, descChoose) = self.selectCandidatesToEliminate()
    self.roundInfo[self.R]["action"] = ("eliminate", elimList)
    descTrans = self.transferVotesFromCandidates(elimList)
    self.roundInfo[self.R]["eliminate"] = descTrans + descChoose
    self.updateTree(self.tree, self.losers)
    self.copyKeepFactors()
    
  def selectCandidatesToEliminate(self):
    "Eliminate any losing candidates."
    
    if self.inInfiniteLoop():
      (c, desc) = self.breakWeakTie(self.R-1, self.continuing, "fewest",
                                    "candidates to eliminate")
      desc = "Candidates tied within precision of computations. " + desc
      self.newLosers([c])
      self.firstEliminationRound = False
      return [c], desc

    else:
      return STV.selectCandidatesToEliminate(self)

  def transferVotesFromCandidates(self, elimList):
    "Eliminate any losing candidates."
    
    elimList.sort()
    desc = "Count after eliminating %s and transferring votes. "\
           % self.b.joinList(elimList)
    return desc

  def copyKeepFactors(self):
    "Udpate the candidate keep factors."

    for c in self.continuing | self.winners:
      self.keepFactor[self.R][c] = self.keepFactor[self.R-1][c]

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
        self.roundInfo[self.R]["action"][1].append(c)
        kf, rem = divmod(self.keepFactor[self.R-1][c] * self.thresh[self.R-1],
                      self.count[self.R-1][c])
        if rem > 0: 
          kf += 1
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


