#!/usr/bin/env python
"run an election from the command line with optional profiling"

__revision__ = "$Id: runElection.py 715 2010-02-27 17:00:55Z jeff.oneill $"

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import getopt

from openstv.ballots import Ballots
from openstv.plugins import getMethodPlugins, getReportPlugins

methods = getMethodPlugins("byName", exclude0=False)
methodNames = methods.keys()
methodNames.sort()

reports = getReportPlugins("byName", exclude0=False)
reportNames = reports.keys()
reportNames.sort()

usage = """
Usage:

  runElection.py [-p prec] [-r report] [-t tiebreak] [-w weaktie] [-s seats] 
                 [-P] [-x reps] method ballotfile

  -p: override default precision (in digits)
  -r: report format: %s
  -t: strong tie-break method: random*, alpha, index
  -w: weak tie-break method: (method-default)*, strong, forward, backward 
  -s: number of seats (for text-format ballot files)
  -P: profile and send output to profile.out
  -x: specify repeat count (for profiling)
    *default

  Runs an election for the given method and ballot file. Results are
  printed to stdout. The following methods are available:
%s
""" % (", ".join(reportNames),
       "\n".join(["    " + name for name in methodNames]))

# Parse the command line.
try:
  (opts, args) = getopt.getopt(sys.argv[1:], "Pp:r:s:t:w:x:")
except getopt.GetoptError, err:
  print str(err) # will print something like "option -a not recognized"
  print usage
  sys.exit(1)

profile = False
reps = 1
reportformat = "TextReport"
strongTieBreakMethod = None
weakTieBreakMethod = None
numSeats = None
prec = None
for o, a in opts:
  if o == "-r":
    if a in reportNames:
      reportformat = a
    else:
      print "Unrecognized report format '%s'" % a
      print usage
      sys.exit(1)
  if o == "-p":
    prec = int(a)
  if o == "-s":
    numSeats = int(a)
  if o == "-t":
    if a in ["random", "alpha", "index"]:
      strongTieBreakMethod = a
    else:
      print "Unrecognized tie-break method '%s'" % a
      print usage
      sys.exit(1)
  if o == "-w":
    if a in ["strong", "forward", "backward"]:
      weakTieBreakMethod = a
    else:
      print "Unrecognized weak tie-break method '%s'" % a
      print usage
      sys.exit(1)
  if o == "-P":
    import cProfile
    import pstats
    profile = True
    profilefile = "profile.out"
  if o == "-x":
    reps = int(a)

if len(args) != 2:
  if len(args) < 2:
    print "Specify method and ballot file"
  else:
    print "Too many arguments"
  print usage
  sys.exit(1)

name = args[0]
bltFn = args[1]

if name not in methodNames:
  print "Unrecognized method '%s'" % name
  print usage
  sys.exit(1)

try:
  dirtyBallots = Ballots()
  dirtyBallots.loadKnown(bltFn, exclude0=False)
  if numSeats:
    dirtyBallots.numSeats = numSeats
  cleanBallots = dirtyBallots.getCleanBallots()
except RuntimeError, msg:
  print msg
  sys.exit(1)

def doElection(reps=1):
  "run election with repeat count for profiling"
  for i in xrange(reps):
    e = methods[name](cleanBallots)
    if strongTieBreakMethod is not None:
      e.strongTieBreakMethod = strongTieBreakMethod
    if weakTieBreakMethod is not None:
      e.weakTieBreakMethod = weakTieBreakMethod
    if prec is not None:
      e.prec = prec
    e.runElection()
  return e

if profile:
  cProfile.run('e = doElection(reps)', profilefile)
else:
  e = doElection()

r = reports[reportformat](e)
r.generateReport()

if profile:
  p = pstats.Stats(profilefile)
  p.strip_dirs().sort_stats('time').print_stats(50)
