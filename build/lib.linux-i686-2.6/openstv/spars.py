"""Model voters with ranked ballot data and count with various voting systems.

VOTING MODELS

There are three different voting models.

(1) Probability Distribution

If there N candidates, then there are O(N!) possible ballots.  Ballots
need not rank every candidate.  The model is a probability
distribution where each ballot has a certain probability of occurring.
Thus, there are O(N!) parameters in this model.  These parameters can
be estimated by simply counting the occurrences of each ballot.  In one
sense, this model has all the information necessary for modeling
voter preferences, but the number of parameters is prohibitive.

(2) Bigrams

Voters are modeled using first-place probabilities and bigram
probabilities.  First-place probabilities are the probability that a
candidate will be first on the ballot.  Bigram probabilities are the
conditional probabilities that a candidate will be ranked next on the
ballot given the current ranking.  Note that the probability that a
candidate will appear next given that she is also the current candidate
must be zero in this model.  There are O(N^2) parameters.  One can
also choose to include in the model the probability that there is no
next candidate (none of the above or NOTA) given the current
candidate or, alternatively, choose not to model NOTA.

The bigram probabilities can be applied directly to model the second
choices on the ballot.  However, to model the third choices on the
ballot, one must take into account the fact that the first choice can
not appear again as the third choice.  I have chosen to take this into
account by removing previous candidates from the probability
distribution and renormalizing so that the remaining probabilities sum
to one.  There are other logical alternatives that may be implemented
in the future.

The first-place probabilities can be estimated by simply counting the
number of times a candidate is ranked first.  They are represented as
p1[c].  There are two options for estimating bigrams:
    (a) Simply counting the number of occurrences of each pair of first and
    second choices.
    (b) Counting all pairs of consecutive rankings and using the
    Expectation-Maximization algorithm to compute the bigrams.
They are represented as p2[c][d] where c is the current ranking and d
is the next ranking.

On one hand, this model loses informations since trigrams and other
n-grams will contain information that is lacking with just bigrams.
On the other hand, there is redundancy in the separate representations
of p2[c][d] and p2[d][c] that could possibly be eliminated.

(3) Spatial Parameters

This parameterization models voters by representing them as a point in
D-dimensional space.  The median voter is at the origin and the voters
are distributed as a D-dimensional unit gaussian around the origin.
The candidates are also points in the space.  A voter will rank the
closest candidate first on the ballot and rank successive candidates
accordingly.  Note that the axes represent unspecified ideologies.
There are O(ND) parameters where D ranges from 1 to N-1.  Larger D add
redundancy without adding precision to the model.

TRANSITION BETWEEN MODELS

Some transitions are invertible in the limit as the number of ballots
increases to infinity.  These are marked as invertible.

Bigrams -> Ballots: Ballots.generate()
Ballots are generated randomly according to the first-place and bigram
probabilities.  Invertible.

Ballots -> Bigrams: Bigrams.estimate()
Bigrams are estimated with the EM algorithm.

Spars -> Bigrams: Bigrams.generate()
The gaussian space is tessellated into areas of equal probability.
Each area is assigned to the appropriate bigram to estimate the bigram
probabilities.  Invertible?

Bigrams -> Spars: Spars.estimate()
Optimization methods.

Spars -> Ballots: Ballots.generate()
Voters are generated randomly in the D-dimensional space and ballots
are created according to the proximity of the candidates to the voter.
Invertible?
 
Ballots -> Spars: Spars.estimate()
???
"""

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

__revision__ = "$Id: spars.py 693 2010-01-03 19:12:05Z jeff.oneill $"

import re
import string
import math
import os.path
import time
import random
from types import *

import STV

NOTA = 1
noNOTA = 0
eps = STV.eps

##################################################################

def d2(x, y):
  "Compute the euclidean distance between two vectors."
  assert(len(x) == len(y))
  d = sum( [ math.pow(x[i]-y[i], 2) for i in range(len(x)) ] )
  d = math.sqrt(d)
  return d
  
def norm2(x):
  "Compute the 2 norm of a vector."
  n = sum( [ math.pow(x[i], 2) for i in range(len(x)) ] )
  n = math.sqrt(n)
  return n

def entropy(x):
  "Compute the entropy of a probability distribution."

  e = 0.0
  assert(abs(sum(x)-1) < eps)
  for p in x:
    assert(p >= 0 and p <= 1)
    if p > 0:
      e -= p * math.log(p)
  return e

def probDist(n, low = 0.8, high=1.0):
  """Generate a probability distribution randomly in an entropy range.

  Returns a vector of length n where each element is in [0,1] and the
  vector sums to 1.  The vector will be in an entropy range bounded
  by low and high.  Low and high correspond to fractions of the
  maximum possible entropy, which occurs for the vector where all
  elements are 1/n.

  The most obvious way to generate the probabilities would be:
    x = []
    for i in range(n-1):
      x.append(random.uniform(0, 1-sum(x))
    x.append(1-sum(x))
  However, this is quite unsatisfactory since the random variables
  are not independent.  A better way is to generate angles and
  convert them to the probabilities.
    sum{p[i]} = 1
    tan(a[i]) = p[i]/p[n]   for i != n
  thus
                    1
    p[n] = --------------------
           1 + sum{ tan(a[i]) }
    p[i] = p[n] * tan(a[i])   for i != n
  This is only an approximation to a uniform distribution but it is
  accurate for higher entropies.  The rejection method is used to
  get probabilities in the desired entropy range."""

  if high > 1.0 or high < low or low < 0.0:
    raise RuntimeError, "high and low must be in [0,1]."

  eMax = entropy([1.0/n]*n)
  eLow = eMax * low
  eHigh = eMax * high

  e = -1
  while not (e < eHigh and e > eLow):
    angles = []
    for i in range(n-1):
      angles.append(random.uniform(0, math.pi/2))
    sumtan = sum([math.tan(i) for i in angles])
    x = [1.0/(1+sumtan)]
    for i in range(n-1):
      x.append(x[0]*math.tan(angles[i]))
    e = entropy(x)
  return x

def pickOne(p, candidates):
  """Randomly pick one thing from a list according to a prob dist.

  p is a probability distribution that can be an array or a
  dictionary.  candidates will be a subset of the array indices
  or the dictionary keys.  Renormalizes the probability
  distribution according the candidate subset and returns one of
  the candidates.  If NOTA is used it should be one of the
  candidates.  If all the candidates have probability 0 then
  return ""."""
  
  s = 0
  for c in candidates:
    s += p[c]
  x = random.uniform(0, s)
  a = 0
  for c in candidates:
    if x >= a and x < a + p[c]:
      return c
    a += p[c]

  # This will happen if all candidates have probability 0.
  return ""


##################################################################

class Spars:
  """Class for working with a spatial parameterization.
  
  Initialize with Spars(d) where d is the number of dimensions.
  c is an array containing the names of the candidates.  p is a
  dictionary containing the parameters which are coordinates in the
  d dimensional space."""
  
  def __init__(self, d=2):
    self.pars = "spars"
    self.d = d # dimensions
    self.c = [] # candidates
    self.p = {} # coordinates (parameters)
    self.bins = []
    self.ngrid = 0

###
    
  def genCoord(self, a=1):
    "Generate a coordinate from Gaussian(0,a) distribution."
    p = []
    for i in range(self.d):
      p.append(random.gauss(0, a))
    return p

  def random(self, n, a=0.5, norm='none'):
    "Generate coordinates for n candidates from a Gaussian distribution."

    self.c = []
    self.p = {}
    
    for i in range(n):
      self.c.append(str(i))
      self.p[str(i)] = self.genCoord(a)

    if norm == 'none':
      return
    elif norm == 'last':
      last = self.c[-1]
      self.p[last] = [0] * self.d
      for c in self.c[0:-1]:
        for d in range(self.d):
          self.p[last][d] -= self.p[c][d]
    elif norm == 'shift':
      mean = [0] * self.d
      for d in range(self.d):
        for c in self.c:
          mean[d] += self.p[c][d]
        mean[d] /= len(self.c)
        for c in self.c:
          self.p[c][d] -= mean[d]
    else:
      raise RuntimeError, "No such normalization."    

  def orderByDistance(self, x):
    "Return a list of canidates in order of proximity to a point."

    cList = []
    available = self.c[:]

    while available != []:
      minDist = 1e10
      closest = ""

      # choose the closest candidate to the voter
      for c in available:
        dist = d2(x, self.p[c])
        if dist < minDist:
          closest = c
          minDist = dist
      assert(closest != "")

      cList.append(closest)
      available.remove(closest)

    return cList

  def grid(self, n):
    "Create a grid of equiprobable regions for a 2D gaussian."

    self.ngrid = n*n

    # compute the centers of bins in the radial direction
    r = []
    for i in range(1, 2*n, 2):
      p = 1.0*i/2/n # P within a disk of radius R
      r.append( math.sqrt(-2*math.log(1-p)) )

    # compute the centers of bins in angle
    a = []
    for i in range(n):
      a.append( 2*math.pi*i/n)

    # convert these to x,y coords
    self.bins = []
    for i in range(n):
      for j in range(n):
        x = r[i]*math.cos(a[j] + (i%2)*math.pi/n)
        y = r[i]*math.sin(a[j] + (i%2)*math.pi/n)
        self.bins.append([x, y])

  def estimate(self, g):
    "Estimate spatial parameters from bigrams."
    # also do this from ballots
    

  def display(self, ybins=10, cutoff=1.0, v=""):
    """Display candidates in two-dimensions using ascii characters.

    2*ybins+1 is the number of vertical ascii characters to use.
    xbins is set to 2*ybins and similarly 2*xbins+1 is the number of
    horizontal characters to use.  This gives a decent aspect ratio
    with most default fonts.  cutoff is the value at the largest xbin
    and ybin."""

    xbins = 2*ybins # gives a decent aspect ratio

    if self.d != 2:
      raise RuntimeError, "Only implemented for two dimensions."

    # create the background axis
    graph = []
    for i in range(2*ybins+1):
      if i == ybins:
        row = (["-"] * xbins) + ["+"] + (["-"] * (xbins-1)) + ["-"]
      else:
        row = ([" "] * xbins) + ["|"] + ([" "] * (xbins-1)) + [" "]
      graph.append(row)

    # put the candidates on the graph
    for c in self.c:
      x = int(round(self.p[c][0]*xbins/cutoff))
      x = max(x, -xbins)
      x = min(x, xbins)
      x += xbins

      y = -int(round(self.p[c][1]*ybins/cutoff))
      y = max(y, -ybins)
      y = min(y, ybins)
      y += ybins

      graph[y][x] = c[-1]

    # if specified, put some voters on the graph too
    if v != "":
      x = int(round(v[0]*xbins/cutoff))
      x = max(x, -xbins)
      x = min(x, xbins)
      x += xbins

      y = -int(round(v[1]*ybins/cutoff))
      y = max(y, -ybins)
      y = min(y, ybins)
      y += ybins

      graph[y][x] = "*"
      
    # display the graph
    for i in range(2*ybins+1):
      print string.join(graph[i], "")

##################################################################

class Bigrams:
  """Class for working with bigram probabilities.

  Initialize with Bigrams(NOTA) or Bigrams(noNOTA).

  NOTA       -- Can be 0 or 1.  If 1 then p2[c][NOTA] is used, otherwise
                it is not.
  fName      -- File name where the bigram data is stored.
  c          -- List of all the possible candidates.
  p1         -- Dictionary that gives the probability that a candidate
                will be first on a ballot.
                  P(c is first) = p1[c]
  p2         -- Dictionary that gives the conditional probability for
                the subsequent candidate on the ballot.
                  P(d is next candidate|c is current candidate) = p2[c][d]
  plength    -- Probabilities for the length of each ballot.
  comment    -- Some information as to where the data came from.
"""

  def __init__(self, mode):
    self.pars = "bigrams"
    self.NOTA = mode
    self.fName = ""
    self.c = []
    self.plength = []
    self.p1 = {}
    self.p2 = {}
    self.comment = ""

  def load(self, fName):
    "Load bigrams from a file."

    self.fName = fName
    self.comment = "Bigrams from %s." % self.fName
    f = open(self.fName, "r")

    x = f.readline()
    x = x.strip()
    if x == "NOTA = 1":
      self.NOTA = 1
    elif x == "NOTA = 0":
      self.NOTA = 0
    else:
      raise RuntimeError, "Bad format in bigram file: %s" % (x)

    # load candidate names
    x = f.readline()
    self.c = x.split()
    n = len(self.c)

    # load probability of ballot lengths
    self.plength = [0]*n
    for i in range(n):
      x = f.readline()
      y = re.match(r"\s*P\s*\(\s*len\s*=\s*(\d+)\s*\)\s*=\s*(0?\.\d+)", x)
      if y is None:
        raise RuntimeError, "Bad format in bigram file %s: %s" % (fName, x)
      if int(y.group(1)) != i+1:
        raise RuntimeError, "Bad format in bigram file %s: %s" % (fName, x)
      p = float(y.group(2))
      self.plength[i] = p

    # check that they add to 1
    s = sum(self.plength)
    if abs(s-1) > eps:
      raise RuntimeError, "Length probabilities must sum to exactly 1."

    # load p1 and p2
    for i in range(n):
      x = f.readline()
      y = re.match(r"\s*P\s*\(\s*(\S+)\s*\)\s*=\s*(0?\.\d+)", x)
      if y is None:
        raise RuntimeError, "Bad format in bigram file %s: %s" % (fName, x)
      c = y.group(1)
      p = float(y.group(2))
      if c not in self.c:
        raise RuntimeError, "Bad format in bigram file %s: %s" % (fName, x)
      self.p1[c] = p
      self.p2[c] = {}

      for j in range(n-1):
        x = f.readline()
        y = re.match(r"\s*P\s*\(\s*(\S+)\s*\|\s*(\S*)\s*\)\s*=\s*(0?\.\d+)", x)
        if y is None:
          raise RuntimeError, "Bad format in bigram file %s: %s" % (fName, x)
        if c != y.group(2):
          raise RuntimeError, "Bad format in bigram file %s: %s" % (fName, x)
        c2 = y.group(1)
        p = float(y.group(3))
        if (c2 not in self.c) or (c == c2):
          raise RuntimeError, "Bad format in bigram file %s: %s" % (fName, x)
        self.p2[c][c2] = p

    f.close()

    # add NOTA if necessary
    if self.NOTA:
      for c in self.c:
        s = sum(self.p2[c].values())
        if s > 1:
          raise RuntimeError, "Conditional probabilities for %s sum to greater than 1." % (c)
        self.p2[c]["NOTA"] = 1 - s

    s = sum(self.p1.values())
    if abs(s-1) > eps:
      raise RuntimeError, "First place probabilities must sum to exactly 1."

    for c in self.c:
      s = sum(self.p2[c].values())
      if abs(s-1) > eps:
        raise RuntimeError, "Conditional probabilities for %s must sum to exactly 1." % (c)

  def save(self, fName):
    "Save bigrams to a file."

    self.fName = fName
    if os.path.exists(fName):
      raise RuntimeError, "I won't overwrite the file: " + fName

    f = open(fName, "w")

    if self.NOTA:
      f.write("NOTA = 1\n")
    else:
      f.write("NOTA = 0\n")

    f.write(string.join(self.c) + "\n")

    for i in range(len(self.c)):
      f.write("P(len=%d) = %s\n" % (i+1, str(self.plength[i])))

    for c in self.c:
      f.write("P(%s) = %s\n" % (c, str(self.p1[c])))
      for d in self.c:
        if c == d:
          continue
        f.write("  P(%s|%s) = %s\n" % (d, c, str(self.p2[c][d])))

    f.close()

  def display(self):
    "Print the bigrams in a nice format."

    print " " * 8 + "|",
    for c in self.c:
      print "%-5.5s" % (c),
    if self.NOTA:
      print "NOTA"
    else:
      print
    print ("-" * 8) + "+" + "-" * (6*(len(self.c)-1+self.NOTA) + 6)

    print "%-8.8s|" % "plen",
    tmp = self.plength[:]
    for c in self.c:
      print "%.3f" % tmp.pop(0),
    print
    print ("-" * 8) + "+" + "-" * (6*(len(self.c)-1+self.NOTA) + 6)

    print "%-8.8s|" % "first",
    for c in self.c:
      print "%.3f" % self.p1[c],
    print
    print ("-" * 8) + "+" + "-" * (6*(len(self.c)-1+self.NOTA) + 6)

    for c in self.c:
      print "%-8.8s|" % c,
      for d in self.c:
        if c == d:
          print "     ",
        else:
          print "%.3f" % (self.p2[c][d]),
      if self.NOTA:
        print "%.3f" % self.p2[c]["NOTA"]
      else:
        print

    print

  def initP2Dict(self):
    "Initializes a dict for the bigram probabilities."
    p2 = {}
    for c in self.c:
      p2[c] = {}
      choices = self.c[:]
      if self.NOTA:
        choices.append("NOTA")
      choices.remove(c)
      for d in choices:
        p2[c][d] = 0.0
    return p2

  def maxP2Diff(self, p2, q2):
    "Computes the maximum difference between two sets of bigrams."
    maxDiff = abs(p2[self.c[0]][self.c[1]] - 
              q2[self.c[0]][self.c[1]])
    for c in self.c:
      for d in p2[c].keys():
        diff = abs(p2[c][d] - q2[c][d])
        if diff > maxDiff:
          maxDiff = diff
    return maxDiff

  def estimate(self, ballots, levels=1, verbose=0):
    "Estimate bigrams from ballot data."

    self.c = ballots.c
    self.comment = "Bigrams estimated from ballot data.\n"
    self.comment += "Ballot data file was: " + ballots.fName + ".\n"
    self.comment += "Comments from that file are:\n"
    self.comment += ballots.comment

    #
    # Estimate first place probabilities and count ballot lengths
    #

    count = {}
    self.p1 = {}
    for c in self.c:
      count[c] = 0
      
    countlength = [0]*len(self.c)
    self.plength = [0]*len(self.c)

    for weight, ballot in ballots.getWeightedBallots():
      count[ballot[0]] += weight
      countlength[len(ballots) - 1] += weight

    for c in self.c:
      self.p1[c] = 1.0*count[c]/ballots.n
    for i in range(len(self.c)):
      self.plength[i] = 1.0*countlength[i]/ballots.n

    #
    # Estimate conditional probabilities
    #

    if ( (type(levels) is not IntType) or 
         (levels not in range(1, len(self.c)-1)) ):
      raise RuntimeError, "Parameter 'levels' must be an integer between 1 and len(candidates)-2, inclusive."

    # Fill in big data structure with all partial counts
    par_count = []
    for level in range(levels):
      par_count.append({})
      
      for weight, ballot in ballots.getWeightedBallots():

        if ( (self.NOTA and len(ballots) < level+1) or
             (not self.NOTA and len(ballots) < level+2) ):
          continue # ballot is too short

        current = ballot[level]
        if not par_count[level].has_key(current):
          par_count[level][current] = {}

        if level == 0:
          previous = ""
        else:
          tmp = ballot[:level]
          tmp.sort()
          previous = string.join(tmp)
        if not par_count[level][current].has_key(previous):
          par_count[level][current][previous] = {}

        if len(ballot[i]) < level+2:
          next = "NOTA"
        else:
          next = ballot[level+1]
        if not par_count[level][current][previous].has_key(next):
          par_count[level][current][previous][next] = 0

        par_count[level][current][previous][next] += weight

    # Initialize with a uniform distribution.
    # Can't initialize with level 0 data because zeros in the p2
    # matrix can cause nasty singularities (see below).
    self.p2 = self.initP2Dict()
    for c in self.c:
      for d in self.p2[c].keys():
        self.p2[c][d] = 1.0/len(self.p2[c].keys())

    while(1):

      # E-Step: Use the current estimate to fill in missing counts.
      #
      # let i,j iterate over candidates with missing counts
      # let c[i] be the missing counts that we need to compute
      # let p[i] be the current estimate for the cond. prob. (p2[c][d])
      # let sc be the sum of the known counts
      # compute the missing counts as:
      #   c[i] =   p[i] * sc
      #          -------------
      #          1 - sum(p[j])

      count = self.initP2Dict()
      for level in range(levels):
        for c in par_count[level].keys():
          for prev in par_count[level][c].keys():

            # add partial counts
            for d in par_count[level][c][prev].keys():
              count[c][d] += par_count[level][c][prev][d]

            missing = prev.split()

            # compute sc from above
            sc = sum(par_count[level][c][prev].values())

            # compute sum(p[j]) from above
            sp = 0
            for d in missing:
              sp += self.p2[c][d]

            # compute and add missing counts
            assert(sp < 1.0)
            for d in missing:
              count[c][d] += 1.0 * self.p2[c][d] * sc / (1 - sp)
            # This will fail if p2[Jim][Mary] = 1.0 after level=0
            # and we get a ballot like [Mary Jim Alice] for level=1.
            # This can happen if we initialize with level 0 data
            # but shouldn't happen if we initialize with uniform data.

      # M-Step: Use the counts to re-estimate.
      p2 = self.initP2Dict()
      for c in self.c:
        s = sum(count[c].values())
        for d in p2[c].keys():
          p2[c][d] = 1.0 * count[c][d] / s

      maxDiff = self.maxP2Diff(self.p2, p2)
      self.p2 = p2
      if verbose:
        self.display()
      if maxDiff < 0.001 or levels == 1:
        break

  def generate(self):
    "Compute bigrams from spars."

    g = Bigrams(noNOTA)
    g.c = self.c
    for c in g.c:
      g.p1[c] = 0.0
    g.p2 = g.initP2Dict()
    g.plength = [0.0] * len(g.c)

    for i in range(len(self.bins)):
      cList = self.orderByDistance(self.bins[i])
      first = cList[0]
      second = cList[1]
      g.p1[first] += 1
      g.p2[first][second] += 1

    for c in self.c:
      g.p1[c] /= self.ngrid
      p2sum = sum(g.p2[c].values())
      for d in g.p2[c].keys():
        g.p2[c][d] /= p2sum

    return g

  def random(self, candidates, low=0.8, high=1.0, maxNOTA=0.05):
    "Generate bigrams randomly in an entropy range."

    self.c = candidates
    self.comment = "Generated randomly with entropy range [%3.1f, %3.1f]" % (low, high)
    self.p1 = {}
    x = probDist(len(candidates), low, high)
    for c in candidates:
      self.p1[c] = x.pop()
    e = entropy(self.p1.values()) # check for validity!

    self.p2 = self.initP2Dict()
    for c in candidates:
      if self.NOTA:
        self.p2[c]["NOTA"] = random.uniform(0, maxNOTA)
      x = probDist(len(candidates)-1, low, high)
      for d in candidates:
        if c == d:
          continue
        self.p2[c][d] = x.pop()
        if self.NOTA:
          self.p2[c][d] *= (1 - self.p2[c]["NOTA"])
      e = entropy(self.p2[c].values()) # check for validity!

##################################################################

class Ballots(STV.Ballots):
  """Class for working with ballot data.

  fName      -- File name where the ballot data is stored.
  c          -- List of all the possible candidates.
  n          -- Number of ballots.
  raw        -- List of all ballots.
  packed     -- List of unique ballots.
  weight     -- Number of times that each packed ballot occurred.
  comment    -- Some information as to where the data came from.
  """

  def generate(self, n, model):
    "Wrapper routine for generating ballots from different models."

    self.n = n # number of ballots to generate
    self.c = model.c
    self.nCand = len(self.c)
    self.raw = []

    self.comment = "Ballots generated randomly on " 
    self.comment += time.strftime("%x %X %Z") + ".\n"
    self.comment += "Parameters are %s.\n" % (model.pars)

    for i in range(n):
      if model.pars == "bigrams":
        ballot = self.genFromBigrams(model)
      elif model.pars == "spars":
        ballot = self.genFromSpars(model)
      else:
        raise RuntimeError, "Can't generate ballots from this object."
      self.raw.append(ballot)

    self.pack()

  def genFromBigrams(self, bigrams):
    """Generate one ballot from bigram probabilities.

    For bigrams without NOTA, there is no modelling of the ballot
    length so the ballots will generally rank all of the candidates.
    A candidate will not be listed only if p[c][d]=0.  I should think
    of a good way to model ballot length when NOTA isn't used.  For
    bigrams with NOTA, the ballot length is easy."""

    ballot = []
    available = self.c[:]

    c = pickOne(bigrams.p1, available)
    assert(c != "NOTA" and c != "")

    if bigrams.NOTA:
      available.append("NOTA")

    while c != "NOTA" and c != "":
      ballot.append(c)
      available.remove(c)
      c = pickOne(bigrams.p2[c], available)

    return ballot

  def genFromSpars(self, spar):
    """Generate one ballot from spatial parameters.

    There is no modeling of the ballot length so the ballots will rank
    all of the candidates.  I should think of a good way of modeling
    ballot length."""

    x = spar.genCoord() # get the coordinate for the voter
    ballot = spar.orderByDistance(x)
    return ballot

###
      
  def KLDist(self, b, r=1):
    """Compute the "distance" between two sets of ballots.

    Compute the "distance" between ballots self.b and b by modeling
    them as probability distributions and using the Kullback-Leibler
    divergence measure.  r is the number or rankings to use in
    creating the probability distributions.  The KL divergence is not
    symmetric so b1.KLDist(b2) is different from b2.KLDist(b1).

    The KL divergence goes to infinity if for any x, q[x] = 0 and p[x]
    != 0.  To avoid this, q is initialized with a count of 1 instead
    of 0.  This is somewhat like using a Bayesian estimate and
    imposing a prior uniform distribution.  This is a hack and should
    be reexamined.  """
    
    if self.c != b.c:
      raise RuntimeError, "Ballots have different candidates."

    nc = len(self.c)

    # estimate the probability distribution for self
    count1 = [0] * pow(nc, r) # infinity not a problem here
    for weight, ballot in self.getWeightedBallots():
      if len(ballot) < r:
        continue
      index = 0
      for j in range(r):
        index += self.c.index(ballot[j]) * pow(nc, j)
      count1[index] += weight
    s1 = 1.0*sum(count1)

    # estimate the probability distribution for b
    count2 = [1] * pow(nc, r) # avoid infinity!
    for weight, ballot in b.getWeightedBallots():
      if len(ballot) < r:
        continue
      index = 0
      for j in range(r):
        index += b.c.index(ballot[j]) * pow(nc, j)
      count2[index] += weight
    s2 = 1.0*sum(count2)

    # compute the KL divergence
    I = 0
    for i in range(len(count1)):
      if count1[i] > 0:
        I += count1[i]/s1 * math.log( (count1[i]/s1) / (count2[i]/s2) )
    return I
