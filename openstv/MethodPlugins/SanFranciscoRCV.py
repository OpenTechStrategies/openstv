"Plugin module for San Francisco's implementation of RCV"

## Copyright (C) 2010 Jeffrey O'Neill
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

__revision__ = "$Id: SanFranciscoRCV.py 821 2010-11-19 23:36:17Z jeff.oneill $"

from openstv.STV import NoSurplusSTV
from openstv.plugins import MethodPlugin

##################################################################

class SanFranciscoRCV(NoSurplusSTV, MethodPlugin):
  "San Francisco's implementation of ranked choice voting"

  methodName = "SanFranciscoRCV"
  longMethodName = "San Francisco RCV"
  status = 1

  htmlBody = """
<p>San Francisco enacted instant runoff voting in 2002, and uses the
name ranked choice voting.  San Francisco's first election with ranked
choice voting was in 2004 and it has been used annually since then.
San Francisco's charter governing ranked choice voting elections is
shown below.</p>

<hr>

<p align=center>SEC. 13.102. - INSTANT RUNOFF ELECTIONS.</p>

<p>(a) For the purposes of this section: (1) a candidate shall be
deemed "continuing" if the candidate has not been eliminated; (2) a
ballot shall be deemed "continuing" if it is not exhausted; and (3) a
ballot shall be deemed "exhausted," and not counted in further stages
of the tabulation, if all of the choices have been eliminated or there
are no more choices indicated on the ballot. If a ranked-choice ballot
gives equal rank to two or more candidates, the ballot shall be
declared exhausted when such multiple rankings are reached. If a voter
casts a ranked-choice ballot but skips a rank, the voter's vote shall
be transferred to that voter's next ranked choice.</p>

<p>(b) The Mayor, Sheriff, District Attorney, City Attorney,
Treasurer, Assessor-Recorder, Public Defender, and members of the
Board of Supervisors shall be elected using a ranked-choice, or
"instant runoff," ballot. The ballot shall allow voters to rank a
number of choices in order of preference equal to the total number of
candidates for each office; provided, however, if the voting system,
vote tabulation system or similar or related equipment used by the
City and County cannot feasibly accommodate choices equal to the total
number of candidates running for each office, then the Director of
Elections may limit the number of choices a voter may rank to no fewer
than three. The ballot shall in no way interfere with a voter's
ability to cast a vote for a write-in candidate.</p>

<p>(c) If a candidate receives a majority of the first choices, that
candidate shall be declared elected. If no candidate receives a
majority, the candidate who received the fewest first choices shall be
eliminated and each vote cast for that candidate shall be transferred
to the next ranked candidate on that voter's ballot. If, after this
transfer of votes, any candidate has a majority of the votes from the
continuing ballots, that candidate shall be declared elected.</p>

<p>(d) If no candidate receives a majority of votes from the
continuing ballots after a candidate has been eliminated and his or
her votes have been transferred to the next-ranked candidate, the
continuing candidate with the fewest votes from the continuing ballots
shall be eliminated. All votes cast for that candidate shall be
transferred to the next-ranked continuing candidate on each voter's
ballot. This process of eliminating candidates and transferring their
votes to the next-ranked continuing candidates shall be repeated until
a candidate receives a majority of the votes from the continuing
ballots.</p>

<p>(e) If the total number of votes of the two or more candidates
credited with the lowest number of votes is less than the number of
votes credited to the candidate with the next highest number of votes,
those candidates with the lowest number of votes shall be eliminated
simultaneously and their votes transferred to the next-ranked
continuing candidate on each ballot in a single counting
operation.</p>

<p>(f) A tie between two or more candidates shall be resolved in
accordance with State law.</p>

<p>(g) The Department of Elections shall conduct a voter education
campaign to familiarize voters with the ranked-choice or, "instant
runoff," method of voting.</p>

<p>(h) Any voting system, vote tabulation system, or similar or
related equipment acquired by the City and County shall have the
capability to accommodate this system of ranked-choice, or "instant
runoff," balloting.</p>

<p>(i) Ranked choice, or "instant runoff," balloting shall be used for
the general municipal election in November 2002 and all subsequent
elections. If the Director of Elections certifies to the Board of
Supervisors and the Mayor no later than July 1, 2002 that the
Department will not be ready to implement ranked-choice balloting in
November 2002, then the City shall begin using ranked-choice, or
"instant runoff," balloting at the November 2003 general municipal
election.</p>

<p>If ranked-choice, or "instant runoff," balloting is not used in
November of 2002, and no candidate for any elective office of the City
and County, except the Board of Education and the Governing Board of
the Community College District, receives a majority of the votes cast
at an election for such office, the two candidates receiving the most
votes shall qualify to have their names placed on the ballot for a
runoff election held on the second Tuesday in December of 2002.</p>
"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    NoSurplusSTV.__init__(self, b)
    MethodPlugin.__init__(self)

    self.batchElimination = "Losers"
    self.weakTieBreakMethod = "strong"
