"""Module for working with ballot data"""

## Copyright (C) 2003-2010  Jeffrey O'Neill
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

__revision__ = "$Id: ballots.py 821 2010-11-19 23:36:17Z jeff.oneill $"

import os
from openstv.plugins import getLoaderPlugins, getLoaderPluginClass

##################################################################

class Ballots(object):
  """Class for working with ballot data.
  
  A Ballots object is concetptually a list of ballots.
  
  A ballot is a list of rankings, with an optional ID.  A ranking is typically
  a candidate index number, but can also be -1 (skipped ranking) or a list of
  candidate index numbers (equal rankings).
  
  Only unique ballots are stored, and the list of ballots is a list of pointers
  to the appropriate ballot.  For methods where the outcome can depend on the
  order of the ballots (e.g., Cambridge STV) the individual ballots are used,
  but for methods where the outcome is independent of the order, only the 
  unique ballots are used along with a weight (the number of times that ballot
  appears).
  
  A ballots object may only contain valid ballot data.  If the ballot data
  contains an error (e.g., a candidate index number that is out of range), an
  error should be raised immediately.
  """

  def __init__(self, customBallotIDs=False):

    self.title = "Title" # An election title.
    self.date = ""       # The date of the election.
    self.numSeats = 1    # The number of seats to be filled.
    self.customBallotIDs = customBallotIDs # Whether custom ballot IDs are
    # used.  If fale, the ballot IDs are just 1 to N.
    self.exceptionQueue = None # Used to erport exceptions back to GUI
    self.dirtyBallots = None # For clean ballots this is a pointer to the 
                             # dirty ballots from which they were created

    self._names = []
    self._n2i = {}
    # A list of candidate names.  The index for a particular name is the
    # candidate number.  The first name is thus assigned to candidate
    # number 0. _n2i is a shortcut for getting the inedex from the name.

    self.withdrawn = []
    # A list of the candidates who are withdrawn from the election, specified
    # by the candidate number.

    # Conceptually each ballot is a list of candidates and each ballot has
    # a ballot ID used to identify that ballot.  Where no ballot IDs are
    # provided, ballots are assigned IDs in numerical order.

    # Note that ballotIDs are assigned to individual ballots and not to
    # weighted ballots.  Where a ballot file specifies a weighted ballot,
    # then a number of individual ballots will be included and each individual
    # ballot will be given a ballotID.

    # In any ballot list, many of the ballots will be identical so, instead
    # of storing each ballot, only unique ballots will be stored.

    self.uniqueBallots = []
    # This is a list of unique ballots.  Each item of the list is a ballot,
    # and each ballot is a list of candidate numbers that represent the
    # candidates being ranked.  For example, if a ballot is [2 4 1], then
    # candidate number 2 is ranked first, candidate number 4 is ranked second,
    # and candidate number 1 is ranked third.
    
    self.uniqueBallotCount = []
    # This is the weight for each unique ballot.
    
    self.uniqueBallotIndexToBallotIndices = []
    # This list has the same length as self.uniqueBallots.  Each item of the
    # list is a Python set that contains the indices of self.ballotOrder
    # corresponding to the unique ballot.
    
    self.uniqueBallotsLookup = {}
    # The keys to this dictionary are string representations of unique
    # ballots and the values are the indices into self.uniqueBallots.  This
    # dictionary indicates whether a given ballot has already been seen, and
    # if so, where the ballot exists in self.uniqueBallots.
    
    self.ballotOrder = []
    # The length of this list is the total number of ballots.  Each entry is 
    # the index into self.uniqueBallots of the corresponding ballot.

    self.ballotIDsList = []
    # A list of the ballot IDs in the order specified in the ballot file.
    # If the file does not have ballot IDs, then this list remains empty and
    # the ballotID is computed from the ballot index (1 .. N).

    self.loader = None
    
  def copy(self, copyBallots=True):

    # Documentation for copy module says it doesn't work with arrays
    ballotList = Ballots()
    ballotList.customBallotIDs = self.customBallotIDs
    ballotList.title = self.title
    ballotList.date = self.date
    ballotList.numSeats = self.numSeats
    ballotList.names = self.names[:]
    ballotList.withdrawn = self.withdrawn[:]
    if copyBallots:
      for i in xrange(self.numBallots):
        ballot = self.getBallot(i)
        ballotID = self.getBallotID(i) if self.customBallotIDs else None
        ballotList.appendBallot(ballot, ballotID)
    # Don't want the copy to save to the same file as the original
    ballotList.loader = None

    return ballotList
  
  @property
  def numBallots(self):
    return len(self.ballotOrder)

  @property
  def numWeightedBallots(self):
    return len(self.uniqueBallots)

  def getNumCandidates(self):
    return len(self.names)

  def setNumCandidates(self, numCandidates):
    assert(len(self.names) == 0)
    names = []
    for i in range(numCandidates):
      names.append("Candidate No. %d" % (i + 1))
    self.names = names

  numCandidates = property(getNumCandidates, setNumCandidates)

  def getNames(self):
    return self._names
  
  def setNames(self, names):
    self._names = list(names)
    for index, name in enumerate(names):
      self._n2i[name] = index

  names = property(getNames, setNames)
  
  def checkBallot(self, ballot):
    # Check to make sure ballot data is valid.  At this point only possible
    # errors should be that the candidate number is too large.
    nc = self.numCandidates
    for ranking in ballot:
      if isinstance(ranking, list):
        self.checkBallot(ranking)
      elif ranking > nc - 1:
        raise RuntimeError, "Ballot has invalid data: %s" % str(ballot)
  
  def appendBallot(self, ballot, ballotID=None):
    "Append a ballot to this Ballots object."

    # Check to make sure whether ballot IDs are allowed
    assert((ballotID == None) ^ (self.customBallotIDs)) # XOR
    
    # Not sure if we want to do this.  May make more sense to have the
    # ballot loader do the checking.
    #self.checkBallot(ballot)
    
    # String representation of ballot for determining whether it is unique
    ballotString = str(ballot)

    # Record the ballot ID if there is one
    if ballotID is not None:
      self.ballotIDsList.append(ballotID)

    ballotIndex = len(self.ballotOrder) # Index of the ballot being added
    if ballotString in self.uniqueBallotsLookup:
      # We have seen this ballot before 
      uniqueBallotIndex = self.uniqueBallotsLookup[ballotString]
      self.uniqueBallotIndexToBallotIndices[uniqueBallotIndex].add(ballotIndex)
      self.uniqueBallotCount[uniqueBallotIndex] += 1
    else:
      # We have not seen this ballot before
      self.uniqueBallots.append(ballot)
      self.uniqueBallotCount.append(1)
      uniqueBallotIndex = len(self.uniqueBallots) - 1
      self.uniqueBallotsLookup[ballotString] = uniqueBallotIndex
      self.uniqueBallotIndexToBallotIndices.append(set([ballotIndex]))
    self.ballotOrder.append(uniqueBallotIndex)

  def appendBallotUsingNames(self, ballot, ballotID=None):
    "Append a ballot to this Ballots object."
    ballot2 = []
    for name in ballot:
      ballot2.append(self._n2i[name])
    self.appendBallot(ballot2, ballotID)

  def getWeight(self, i):
    "Return the weight of the ith weighted ballot."
    return self.uniqueBallotCount[i]

  def getWeightedBallot(self, i):
    "Return the ith weighted ballot."

    return (self.uniqueBallotCount[i], self.uniqueBallots[i][:])
    
  def getSortedWeightedBallots(self):
    "This is used to compare two ballot lists for testing purposes."

    # We should replace this with a diff-like function that returns true
    # or false to indicate whether two ballots objects are the same.
    
    sortedBallots = [(str(self.uniqueBallots[i]),
                      self.uniqueBallotCount[i])
                     for i in xrange(self.numWeightedBallots)]
    sortedBallots.sort()
    return sortedBallots

  def getBallot(self, i):
    j = self.ballotOrder[i]
    return self.uniqueBallots[j][:]

  def getBallotID(self, i):
    if self.customBallotIDs:
      return self.ballotIDsList[i]
    else:
      return i + 1

  def getBallotAndID(self, i):
    return (self.getBallot(i), self.getBallotID(i))

  def getBallotsAndIDs(self):
    if self.customBallotIDs:
      ballotIDs = self.ballotIDsList[:]
    else:
      ballotIDs = range(1, self.numBallots + 1)
      
    return zip([self.uniqueBallots[i][:] for i in self.ballotOrder], ballotIDs)

  def setBallot(self, i, ballot):

    # This is an expensive operation but it is only done when the user
    # is editing ballots so it does not need to be done that quickly
    oldBallots = self.getBallotsAndIDs()
    oldBallots[i] = (ballot[:], oldBallots[i][1])
    self.deleteBallots()
    for ballot, ballotID in oldBallots:
      if not self.customBallotIDs:
        ballotID = None
      self.appendBallot(ballot, ballotID)

  def deleteBallot(self, i):

    # This is an expensive operation but it is only done when the user
    # is editing ballots so it does not need to be done that quickly
    oldBallots = self.getBallotsAndIDs()
    oldBallots.pop(i)
    self.deleteBallots()
    for ballot, ballotID in oldBallots:
      if not self.customBallotIDs:
        ballotID = None
      self.appendBallot(ballot, ballotID)
    
  def deleteBallots(self):
    self.uniqueBallots = []
    self.uniqueBallotIndexToBallotIndices = []
    self.uniqueBallotsLookup = {}
    self.ballotIDsList = []
    self.ballotOrder = []

  def getTopChoiceFromBallot(self, i, choices):
    "Return the top choice on a ballot among candidates still in the running."

    j = self.ballotOrder[i]
    ballot = self.uniqueBallots[j]
    for c in ballot:
      if c in choices:
        return c
    return None

  def getTopChoiceFromWeightedBallot(self, i, choices):
    "Return the top choice on a ballot among candidates still in the running."

    ballot = self.uniqueBallots[i]
    for c in ballot:
      if c in choices:
        return c
    return None

  def getCleanBallots(self, removeEmpty=True, removeOvervotes="Cambridge",
                      removeDupes=True, removeWithdrawn=True):
    """Ballots can be cleaned in several ways:
    
    (1) Removing withdrawn candidates.  This is done if withdrawn is not None.
    
    (2) Removing empty ballots.  This is done if removeEmpty is True.
    
    (3) Removing overvotes (more than one candidate is given the same
    ranking).  Possible methods are "Cambridge" (remove overvotes and
    go on to the next valid ranking), "San Francisco" (ballot is
    exhausted at an overvote), "none" (do not remove overvotes).
    
    (4) Remove duplicate rankings (same candidate is ranked more than once on
    a ballot).  This is done if removeDupes is True.
    
    (5) Remove skipped rankings.  A skipped ranking is indicated by a "-1"
    instead of a candidate number.  These are always removed.
    
    (6) Does not currently check for duplicate ballot IDs, but we might want
    to add this later.
    
    """

    # We want to keep track of the link between dirty and clean ballots
    cleanBallots = self.copy(False)
    cleanBallots.withdrawn = []
    cleanBallots.customBallotIDs = True
    cleanBallots.dirtyBallots = self
    
    # Set up a translation list for candidate numbers for removing
    # withdrawn candidates.  c2 = c2c[c] translates an original candidate
    # number "c" to a translated candidate number "c2" taking into account
    # candidates that have been removed from the ballots.  If a candidate is
    # withdrawn, c2c returns None.  
    c2c = range(self.numCandidates)
    if removeWithdrawn:
      n = 0
      for i in range(self.numCandidates):
        if i in self.withdrawn:
          c2c[i] = None
          n += 1
        else:
          c2c[i] -= n

    # Loop over ballots and perform requested cleaning
    for i in xrange(self.numBallots):
      ballot, ballotID = self.getBallotAndID(i)
      seenCandidates = set()
      cleanBallot = [] # This will be a cleaned version of ballot
      for item in ballot:
        
        # Candidate may have to pass two tests to get in the cleaned ballots.
        # First, candidate must not be withdrawn.
        # Second, candidate must not already be on the ballot when removeDupes
        # is true.

        if isinstance(item, list):
          assert(len(item) > 1)
          if removeOvervotes == "Cambridge":
            continue
          elif removeOvervotes == "San Francisco":
            break
          cleanItem = []
          for c in item:
            if c == -1:
              continue  # Skipped ranking
            c2 = c2c[c] # Candidate number after removing withdrawn candidates
            if not ((c in self.withdrawn) or (removeDupes and c2 in seenCandidates)):
              assert(c2 is not None)
              cleanItem.append(c2)
              seenCandidates.add(c2)
          if len(cleanItem) > 1:
            cleanBallot.append(cleanItem)
          elif len(cleanItem) == 1:
            cleanBallot.append(cleanItem[0])
          
        else:
          c = item
          if c == -1:
            continue  # Skipped ranking
          c2 = c2c[c] # Candidate number after removing withdrawn candidates
          if not ((c in self.withdrawn) or (removeDupes and c2 in seenCandidates)):
            assert(c2 is not None)
            cleanBallot.append(c2)
            seenCandidates.add(c2)

      if not removeEmpty or len(cleanBallot) > 0:
        cleanBallots.appendBallot(cleanBallot, ballotID)

    # Remove the withdrawn candidates names
    cleanBallots.names = [self.names[c] for c in range(self.numCandidates)
                          if c not in self.withdrawn]
    
    return cleanBallots

  def appendFile(self, fName):
    "Append ballot data from a file."

    ballotList = Ballots()
    ballotList.loadUnknown(fName)
    
    if (ballotList.numSeats != self.numSeats or
        ballotList.names != self.names or
        ballotList.withdrawn != self.withdrawn):
      raise RuntimeError, \
            "Can't append ballots.  The numbers of seats and candidates, \n"\
            "the names of the candidates, and the withdrawn candidates \n"\
            "must be identical."

    for i in xrange(ballotList.numBallots):
      ballot = ballotList.getBallot(i)
      ballotID = ballotList.getBallotID(i) if self.customBallotIDs else None
      self.appendBallot(ballot, ballotID)

  def save(self):
    "Save back to the last file I was saved or loaded from"
    self.loader.save(self)

  def saveAs(self, fName, packed=False):
    "Create a new ballot loader and save ballots"
    
    extension = os.path.splitext(fName)[1][1:]
    loaderClass = getLoaderPluginClass(extension)
    if loaderClass is None:
      # If we don't know then the default is blt format
      loaderClass = getLoaderPluginClass("blt")
    self.loader = loaderClass()
    self.loader.save(self, fName, packed)

  def loadKnown(self, fName, extension=None, exclude0 = True):
    "Load a file based on its file extension."
    
    if extension is None:
      extension = os.path.splitext(fName)[1][1:]
    loaderClass = getLoaderPluginClass(extension, exclude0)
    if loaderClass is None:
      raise RuntimeError, "Do not know how to load files with extension %s." % (extension)

    self.loader = loaderClass()
    self.loader.load(self, fName)

  def loadUnknown(self, fName, exclude0 = True):
    "Load a file of unknown format."
    
    # Try the loader that claims this extension first.  If that one doesn't 
    # work then we try the others.  Get the loader classes in the right order.
    extension = os.path.splitext(fName)[1][1:]
    loaderClasses = getLoaderPlugins("classes", exclude0)
    bestGuess = getLoaderPluginClass(extension, exclude0)
    if bestGuess is not None:
      loaderClasses.remove(bestGuess)
      loaderClasses.insert(0, bestGuess)

    errorMsg = "Could not load ballots from file %s." % fName
      
    # Try them in order
    for loaderClass in loaderClasses:
      try:
        self.loader = loaderClass()
        self.loader.load(self, fName)
      except RuntimeError, (msg,):
        errorMsg += "\n" + msg.strip()
      else:
        break
    else:
      # None of the ballot loaders succeeded so raise an exception
      if self.exceptionQueue is None:
        raise RuntimeError(errorMsg)
      else:
        self.exceptionQueue.put(errorMsg)

  def getFileName(self):
    "The name of the last file I was saved or loaded from"
    if (self.loader is not None):
      return self.loader.fName
    else:
      return None
     
  def reorderCandidates(self, order=None):
    "Reorder candidates in alphabetical order or the order specified."

    if order == None:
      # Default is alphabetical order
      order = range(self.numCandidates)
      order.sort(key=lambda c: self.names[c])

    # Check to make sure that all candidates are included
    check = order[:]
    check.sort()
    if check != range(self.numCandidates):
      raise RuntimeError, "Must specify all the candidates when reordering."

    # Set up a translation list.
    # order gives the desired candidate order, e.g., [4 0 3 1 2]
    # Thus, we want 4->0, 0->1, 3->2, 1->3, and 2-> 4
    # c2c does this translation
    c2c = [0] * self.numCandidates
    for i, c in enumerate(order):
      c2c[c] = i

    # Translate all the candidate numbers. This must be done in two places:
    # (1) The ballots in uniqueBallots
    # (2) The keys in uniqueBallotsLookup

    # Easier to create a new uniqueBallotsLookup
    self.uniqueBallotsLookup = {}

    # Loop over all the weighted ballots
    for i in xrange(self.numWeightedBallots):
      for j, c in enumerate(self.uniqueBallots[i]):
        self.uniqueBallots[i][j] = c2c[c]
      ballotString = str(list(self.uniqueBallots[i]))
      self.uniqueBallotsLookup[ballotString] = i
      
    # Put the names in the right order
    oldNames = self.names[:]
    names = self.names
    for c in range(self.numCandidates):
      cc = c2c[c]
      names[cc] = oldNames[c]
    self.names = names

  def joinList(self, itemList, convert="names"):

    assert(len(itemList) > 0)

    if convert == "names":
      tmp = itemList[:]
      itemList = [self.names[c] for c in tmp]

    text = " ".join(itemList)
    sep = "; " if text.find(",") != -1 else ", "
    
    if len(itemList) == 1:
      txt = itemList[0]
    elif len(itemList) == 2:
      txt = itemList[0] + " and " + itemList[1]
    else:
      txt = sep.join(itemList[:-1])
      txt += sep + "and " + itemList[-1]
    return txt

  def isalnum(self):
    """Are all candidate names alphanumeric?"""
    for name in self.names:
      if not name.isalnum():
        return False
    return True
  
