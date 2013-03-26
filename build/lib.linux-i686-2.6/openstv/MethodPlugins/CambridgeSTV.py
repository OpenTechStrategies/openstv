"Plugin Module for Cambridge STV"

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

__revision__ = "$Id: CambridgeSTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

import os.path
import string

from openstv.STV import OrderDependentSTV
from openstv.plugins import MethodPlugin
from openstv.ballots import Ballots

##################################################################

class CambridgeSTV(OrderDependentSTV, MethodPlugin):
  "Cambridge STV"

  methodName = "Cambridge STV"
  longMethodName = "Cambridge STV"
  status = 1

  htmlBody = """
<p>The City of Cambridge, Massachusetts has used the single
transferable vote to elect its city council and school committee since
1941.  The statute providing the counting rules is Chapter 54A of
Massachusetts General Laws, the relevant portions of which are
included below.  Note that &#167; 16(b) allows Cambridge to use any method
for transfering surplus votes that was in use in 1938, and Cambridge has
chosen to use the Cincinnati method.</p>

<p>The City of Cambridge describes the Cincinnati method as follows:
The ballots of the candidate who has a surplus are numbered sequentially
in the order in which they have been counted (that is, in the sequence
dictated by the random draw of precincts) and then every <i>n</i>th
ballot is drawn and transferred to a continuing candidate until the
original candidate is credited with ballots equaling no more than
quota. <i>n</i> is nearest whole number computed by the
formula</p>

<p align=center>
<i>n</i> = <u>Candidate's Total Ballots</u><br>
Surplus Ballots.</p>

<p>A ballot selected by this method that does not show a preference for a
continuing candidate is skipped and remains with the original
candidate. If not enough ballots are removed when ballots <i>n, 2n,
3n</i>, .... have been transferred, the sequence starts again with
<i>n+1, 2n+1, 3n+1</i>, ....</p>

<p>For more information, see
http://www.cambridgema.gov/election/Proportional_Representation.cfm.</p>

<p>Since candidates with fewer than 50 votes are eliminated, this
method should not be used with a small number of ballots.  OpenSTV's
implementation of Cambridge STV has been validated against official
Cambridge results from 1999 to present.</p>

<p>OpenSTV provides the option of saving the winning candidates'
ballots to separate files.  The Cambridge rules use these ballots to
elect a replacement candidate in the event of a vacancy.</p>

<hr>

<p align=center><b>Massachusetts General Laws, Chapter 54A</b></p>

<p align=center>ELECTION OF CERTAIN CITY AND TOWN OFFICERS BY
PROPORTIONAL REPRESENTATION OR PREFERENTIAL VOTING</p>

<p><b>&#167; 9. Rules for counting ballots, and determining
results.</b> Ballots cast under proportional representation shall be
counted and the results determined under the supervision of the
director of the count appointed pursuant to section six, according to
the following rules:-</p>

<p>(a) The ballots in each ballot receptacle shall be examined for
validity and those which are found to be blank or otherwise invalid
shall be separated from the valid ballots. The number of valid ballots
from each precinct and the total number of valid ballots shall be
recorded. If a ballot does not clearly show which candidate the voter
prefers to all others, or if it contains any word, mark or other sign
apparently intended to identify the voter, it shall be set aside as
invalid. Every ballot not thus invalid shall be counted according to
the intent of the voter, so far as that can be clearly ascertained,
whether marked according to the directions printed on it or not. No
ballot shall be held invalid because the names of candidates thereon
for whom the voter did not mark a choice have been stricken out,
unless such striking out constitutes an identifying mark. A single
cross on a ballot on which no figure 1 appears shall be considered
equivalent to the figure 1. If a ballot contains both figures and
crosses, the order of the choice shown by the figures shall be taken
as the voter's intention in so far as the order is clearly
indicated. If the consecutive numerical order of the figures on a
ballot is broken by the omission of one or more figures, the smallest
number marked shall be taken to indicate the voter's first choice, the
next smallest his second, and so on, without regard to the figure or
figures omitted.</p>

<p>(b) Each candidate shall be credited with one vote for every valid
ballot that is sorted to him as first choice, or otherwise credited to
him as hereinafter provided, and no ballot shall ever be credited to
more than one candidate at the same time.</p>

<p>(c) A "quota" is the smallest number of votes which any candidate must receive in
order to be assured of election without more candidates being elected
than there are offices to be filled. It shall be determined by
dividing the total number of valid ballots by one more than the total
number of candidates to be elected and adding one to the result,
disregarding fractions. Whenever at any stage of the counting the
number of ballots credited to a candidate becomes equal to the quota,
he shall be declared elected, and no ballots in excess of the quota
shall be credited to him except as provided in rule (f) or (1) of this
section.</p>

<p>(d) The ballots shall be sorted according to the first choices
marked on them, the ballots from each polling place being handled
together, and those from different polling places being handled in the
order of polling places determined under the provisions of section
eight.</p>

<p>(e) If a candidate is elected while the ballots are being sorted
according to first choices, any subsequent ballots which show him as
first choice shall each be credited to the second choice marked on it,
or, if the second choice also has been elected, to the next choice
marked on it for a candidate not yet elected.</p>

<p>(f) If during the first sorting of ballots, ballots are found which
are marked for a candidate already elected as first choice, but show
no clear choice for any unelected candidate, such ballots shall at the
end of the sorting be given to the candidate of their first choice,
and in their place an equal number, as nearly as possible, of the last
ballots sorted to that candidate which show a clear choice for
unelected candidates, all as determined by the director of the count,
shall be taken and re-sorted to unelected candidates as if they were
then being sorted for the first time.</p>

<p>(g) When all the ballots have been thus sorted and credited to the
first available choices marked on them, every candidate who is
credited with fewer ballots than the number of signatures required for
his nomination shall be declared defeated.</p>

<p>(h) All the ballots of the candidates thus defeated shall be
transferred, each to the candidate indicated on it as next choice
among the continuing candidates. A "continuing candidate" is a candidate
not as yet either elected or defeated. Any ballot taken for transfer which
does not clearly indicate any candidate as next choice among the continuing
candidates shall be set aside as "exhausted".</p>

<p>(i) When all the ballots of the candidates thus defeated have
been transferred, the one candidate who is then lowest on the poll
shall be declared defeated and all his ballots transferred in the same
way.</p>

<p>(j) Thereupon the candidate who is then lowest shall be
declared defeated and all his ballots similarly transferred; and in
like manner candidates shall be declared defeated one at a time and
all their ballots transferred.</p>

<p>(k) If, when a candidate is to be declared defeated, two or more
candidates are tied at the bottom of the poll, that one of the tied
candidates shall be declared defeated who was credited with fewest
ballots immediately prior to the last transfer of ballots. If two or
more of the tied candidates were tied at that stage of the count,
also, the second tie shall be decided by referring similarly to the
standing of candidates immediately prior to the last transfer of
ballots before that. This principle shall be applied successively as
many times as may be necessary, a tie shown at any stage of the count
being decided by referring to the standing of the tied candidates
immediately prior to the last preceding transfer of ballots. Any tie
not otherwise provided for shall be decided by lot.</p>

<p>In interpreting this and other rules contained in this section the
transfer of all ballots from candidates defeated together under rule
(g) of this section, and the transfer of all ballots from each
candidate defeated thereafter shall each constitute a single separate
transfer.</p>

<p>(l) Whenever candidates to the number to be elected have received
the quota, any transfer of ballots in progress when the last quota was
reached shall be completed, but immediately thereafter all continuing
candidates shall be declared defeated and the election shall be at an
end. Whenever all ballots of all defeated candidates have been
transferred, and it is impossible to defeat another candidate without
reducing the continuing candidates below the number still to be
elected, all the continuing candidates shall be declared elected and
the election shall be at an end.</p>

<p>(m) A record of the count shall be kept in such form as to show,
after each sorting or transfer of ballots, the number thereby credited
to each candidate, the number thereby set aside as exhausted, the
total for each candidate, the total set aside as exhausted, and the
total number of valid ballots found by adding the totals of all
candidates and the total set aside as exhausted.</p>

<p>(n) Every ballot that is transferred from one candidate to another
shall be stamped or marked so that its entire course from candidate to
candidate can be conveniently traced.</p>

<p>(o) If at any time after the first sorting of the ballots a ballot
is found to have been credited to the wrong candidate, it may be
transferred, as part of the transfer that is in progress, to the
continuing candidate, if any, to whom it should have been credited at
the time the error was made, or, if it should previously have become
exhausted, may be set aside as exhausted as part of the transfer that
is in progress; provided, that if the number of misplaced ballots
found is sufficient to make it possible that any candidate has been
wrongly defeated, so much of the sorting and transferring as may be
required to correct the error shall be done over again before the
count proceeds.</p>

<p>If in correcting an error any ballots are re-sorted or
re-transferred, every ballot shall be made to take the same course
that it took in the original count unless the correction of an error
requires its taking a different course. The principles of the rules of
this section shall apply also to any recount which may be made after
the original count has been completed.</p>

<p>(p) The director of the count and his assistants shall proceed with
reasonable expedition in the counting of the ballots, but may take
recesses at the discretion of the director. The city or town clerk
shall make proper provision for the safekeeping of the ballots while
the counting is not in progress.</p>

<p>(q) The candidates, their witnesses, alternate witnesses and
representatives accredited under section seven, representatives of the
press, and, as far as may be consistent with good order and with
convenience in the counting and transferring of the ballots, the
public shall be afforded every facility for being present and
witnessing the counting and transferring of the ballots.</p>

<p>(r) Each of the candidates entitled to appoint witnesses of the
central count as provided in section seven shall be entitled to
appoint a member of a board of review of the central count. Such
appointment shall be made within the time and in the manner prescribed
for the appointment of such witnesses of the central count. In the
central counting place a board of review so constituted shall be given
facilities for examining all the ballots in the quota of each elected
candidate in order to make sure that all the ballots of such quota are
rightfully credited to the candidate toward whose election they have
been counted, that the number of ballots therein is actually equal to
the quota prescribed in this section, and that"exhausted" ballots have
been properly so designated. Any errors discovered by
such a board of review shall be reported to the director of the
count.</p>

<p>(s) When the election with respect to any particular body or office
is at an end the director of the count shall publicly announce the
result of the vote for such body or office. The provisions of section
one hundred and seven of chapter fifty-four relative to presiding
officers and other election officers at polling places shall, so far
as apt, apply to the director of the count and his assistants with
respect to all ballots, records, copies of records, envelopes and
ballot boxes, transmitted to the central counting place under section
eight and to all other papers, records and apparatus used in counting
the votes at the central counting place, except that ballots cast for
a particular body or office, as well as those spoiled and returned and
those not given out, shall be enclosed, and the envelopes sealed and
delivered or transmitted to the city or town clerk as soon as may be
after the public announcement of the result of the vote for such body
or office.</p>

<p>(t) No canvass or count of the vote shall be made on
the Lord's day.</p>

<p><b>&#167; 10. Ballots; preservation; examination.</b> The ballots
cast at each election by proportional representation or preferential
voting shall be preserved by the city or town clerk until the term of
office of the members of the body or of the officer elected thereby
has expired, and shall be available for examination continuously
throughout the business day, under supervision of the city or town
clerk, on written application signed by not less than one hundred
voters of the city or town and the payment of a fee of twenty-five
dollars for each day on which such inspection is held. Such
application shall name not more than three representatives of the
applicants to make such examination.</p>

<p><b>&#167; 11. Publication of statements regarding ballots cast.</b>
Within thirty days after an election to elect members of a body by
proportional representation or an officer by preferential voting, the
city or town clerk shall cause the ballots cast for such body or
office to be examined and shall publish a statement
showing-</p>

<p>(a) The number of first-choice ballots cast for each candidate at
each polling place.</p>

<p>(b) The number of ballots from each polling place finally counted
for each of the elected candidates.</p>

<p>(c) The number of the exhausted ballots from each polling place
which showed one or more choices for elected candidates and the number
which did not show any such choice.</p>

<p>(d) The number of blank ballots cast for each body or office at
each polling place.</p>

<p>(e) The number of ballots otherwise invalid cast for each body or
office at each polling place.</p>

<p>(f) The number of first choices, second choices, third choices, and
so on, used in the election of each of the elected candidates.</p>

<p>(g) Such other information in regard to the ballots as the city or
town clerk may deem of interest.</p>

<p>A copy of such statement shall be kept on file in the office of the
city or town clerk open to public inspection.</p>

<p><b>&#167; 12. Recount of ballots.</b> Partial or complete recounts
of the ballots cast for any body or office in an election by
proportional representation or by preferential voting shall take place
in the manner provided in sections one hundred and thirty-four to one
hundred and thirty-seven, inclusive, of said chapter fifty-four,
except that any petition shall be submitted on or before five o'clock
in the afternoon of the third day following the public announcement by
the director of the count of the result of the vote for such body or
office and shall be on a form approved and furnished by the city or
town clerk and be signed in a town by ten or more voters of such town,
in a city, except Boston, by fifty or more voters of such city and in
Boston by two hundred and fifty or more voters of said Boston and
except that any such recount in any city or in any town divided into
precincts shall be conducted for the entire city or town instead of
for specified precincts. If a partial or complete recount of the
ballots cast in such an election shall in fact take place, it shall be
conducted according to the rules prescribed for the original count as
nearly as is practicable.

<p><b>&#167; 13. Vacancies in bodies elected by proportional
representation; filling.</b> When a vacancy occurs in an elective body
whose members were elected by proportional representation, such
vacancy shall be filled for the remainder of the unexpired term by a
public recount of the ballots credited at the end of the original
count to the candidate elected thereby whose place has become
vacant. Except for the following special rules, the provisions
governing the original count shall be in effect:</p>

<p>(a) All choices marked for candidates theretofore elected or who
have become ineligible or have withdrawn shall be disregarded:</p>

<p>(b) The ballots shall be sorted each to the earliest choice marked
on it for any of the eligible candidates.</p>

<p>(c) If any candidate has to his credit more than half of the
ballots which show any preference among the eligible candidates he
shall be declared elected to the vacant place.</p>

<p>(d) If no candidate receives more than half of such ballots, the
candidates lowest on the poll shall be declared defeated one after
another and after each candidate is defeated his ballots shall be
transferred among the continuing candidates.</p>

<p>(e) The process hereinbefore provided shall be continued until one
candidate is credited with more ballots than all the other undefeated
candidates together, when he shall be declared elected to the vacant
place.</p>

<p>If a vacancy in an elective body occurs for which no regularly
nominated candidate remains it shall be filled for the unexpired term
by a majority vote of the remaining members; and if but a single
member remains or if a majority vote of the remaining members is not
obtained within thirty days after the vacancy occurs, it shall be
filled by a special election, in the case of a single vacancy, by
preferential voting or, in case two or more vacancies exist at the
same time, by proportional representation.

<p><b>&#167; 14. Ballots; rules for counting where election by
preferential voting.</b> Ballots cast under preferential voting shall
be counted in the central counting place under the supervision of the
director of the count, in accordance with the following
rules:-</p>

<p>(a) The ballots shall first be sorted according to the
first choices marked on them, and the total number of valid ballots
thus sorted to each candidate shall be ascertained. The validity of
ballots shall be determined according to the principles laid down for
the count of ballots in an election by proportional representation in
rule (a) of section nine.</p>

<p>(b) If any candidate is found to have been marked as first choice
on more than half of the valid ballots he shall be declared
elected.</p>

<p>(c) If no candidate is so elected after the count of first choices,
every candidate who is credited with fewer ballots than the number of
signatures required for his nomination shall be declared defeated.</p>

<p>(d) All the ballots of the candidates so defeated shall be
transferred, each to the candidate indicated on it as next choice
among the undefeated candidates. Any ballot taken for transfer which
does not clearly indicate any candidate as next choice among the
undefeated candidates shall be set aside as "exhausted".</p>

<p>(e) If, after this or any subsequent transfer of ballots, one
candidate is credited with more than half of the valid ballots which
have not become exhausted, he shall be declared elected.</p>

<p>(f) If no candidate is so elected after the transfer of the ballots
of candidates defeated under rule (c), the one candidate who is then
lowest on the poll shall be declared defeated and all his ballots
transferred in the same way.</p>

<p>(g) Thereupon, if no candidate is yet elected, the candidate who is
then lowest shall be declared defeated and all his ballots similarly
transferred. Thus candidates shall be deemed defeated one at a time,
and all their ballots transferred until some candidate has received
the necessary majority of the ballots which have not become exhausted
and is accordingly declared elected.</p>

<p>(h) Ties shall be decided, a record of the count kept, errors
corrected, recesses taken, and candidates and others permitted to be
present according to the principles prescribed for elections by
proportional representation in rules (k), (m), (o), (p) and (q) of
section nine.</p>

<p><b>&#167; 15. Vacancies in single elective offices; filling.</b>
All provisions of law from time to time applicable in the case of a
vacancy in an elective office shall continue to apply after the
filling of such office by preferential voting, except that any
election to fill such vacancy shall also be by preferential
voting.</p>

<p><b>&#167; 16. Mechanical or other voting devices; methods of
counting first choices.</b></p>

<p>(a) In conducting any election by proportional representation or
preferential voting, mechanical or other devices may be used, subject,
however, to the provisions of sections thirty-two to thirty-nine,
inclusive, of chapter fifty-four, if the city council or the town
passes a vote providing expressly that such devices shall be used in
such election; and said sections, so far as apt, shall be applicable
in all respects in case of such devices so used. In case such devices
are to be used in any city or town, the city or town clerk may modify
the form of ballot, the rotation of names thereon, the directions to
voters and other details in respect to the election process; provided,
that no change shall be made which will alter or impair the principles
of voting or counting the ballots governing elections by proportional
representation or preferential voting, as the case may be, but the
voter may be limited to not less than fifteen choices for any
particular body or office.</p>

<p>(b) In any city or town where elections by proportional
representation are to be held, any method of counting the
voters' first choices and treating any such choices in excess of
the quota, provided for under any system of proportional
representation which on January first, nineteen hundred and
thirty-eight was in effect for the purpose of municipal elections in
any city of the United States, may be substituted for the method of
counting such choices set forth in this chapter, if the registrars of
voters determine that such substitution is advisable; provided, that
they issue regulations embodying the method so substituted and
provided, further, that such regulations shall not be effective with
respect to any election unless at least thirty days prior thereto
copies of such regulations are available for delivery to such of the
voters as may request them.</p>
"""
  
  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd
  
  def __init__(self, b):
    OrderDependentSTV.__init__(self, b)
    MethodPlugin.__init__(self)
    
    self.batchElimination = "Cutoff"
    self.batchCutoff = 50
    self.threshName = ["Droop", "Static", "Whole"]
    self.delayedTransfer = "Off"
    self.saveWinnersBallots = False
    self.outputDir = None
    self.createGuiOptions(["saveWinnersBallots"])

  def checkMinRequirements(self):
    "Only attempt to count votes if there are enough candidates and voters."
    
    OrderDependentSTV.checkMinRequirements(self)
    if self.b.numBallots < self.batchCutoff * self.numSeats:
      raise RuntimeError, """\
Not enough ballots to run an election.
Need at least %d ballots but have only %d.""" % (
        self.batchCutoff*self.numSeats, self.b.numBallots)
    
  def updateCount(self):
    "Update the vote totals after a transfer of votes."

    for c in range(self.b.numCandidates):
      if c in self.winnersEven:
        # With CambridgeSTV, some winners may have additional votes if a large 
        # number of votes were not transferable (e.g., no next candidate).
        self.count[self.R][c] = self.thresh[self.R-1]
      else:
        self.count[self.R][c] = len(self.votes[c])

  
  def transferSurplusVotesFromCandidate(self, cSurplus):
    "Transfer surplus votes according to the Cambridge rules."
    
    total = self.count[self.R-1][cSurplus]
    surplus = total - self.thresh[self.R-1]
    skip = int(round(1.0 * total / surplus)) # decimation factor
    start = skip - 1                         # starting point

    # compute the order in which ballots will be considered for transfer
    if surplus == 1:
      order = range(total)
      order = order[-1:] + order[:-1]
    else:
      order = []
      for i in range(start, start+skip):
        for j in range(i, total, skip):
          order.append(j)
      for i in range(start):
        order.append(i)

    # transfer the ballots
    nTransferred = 0
    ctng = self.continuing.copy()  # candidates who can receive votes
    # attempt to transfer votes in the precalculated order
    cSurplusVotes = self.votes[cSurplus][:] # use this to loop over c0's votes
    for i in order:   # i is the ith vote of a candidate
      bi = cSurplusVotes[i]  # bi is the bith ballot
      # Get the next candidate.
      # If no next candidate, then the vote is not transferable and
      # remains with the current candidate.
      c = self.b.getTopChoiceFromBallot(bi, ctng)
      if c != None:
        self.votes[c].append(bi)
        # If the receiving candidate is now a winner, then that
        # candidate can no longer receive any more votes.
        if len(self.votes[c]) >= self.thresh[self.R-1]:
          ctng.remove(c)
        self.votes[cSurplus].remove(bi)
        nTransferred += 1
      # Check if the entire surplus has been transferred
      if nTransferred == surplus:
        break

    desc = "Count after transferring surplus votes from %s by using the "\
           "Cincinnati method with a skip value of %d. " \
           % (self.b.names[cSurplus], skip)
    return desc

  def transferVotesFromCandidates(self, elimList):
    "Eliminate candidate according to the Cambridge rules."

    # Get rid of candidates without any votes
    remainingLosers = [c for c in elimList if self.count[self.R-1][c] > 0]
    eliminationOrder = [c for c in elimList if self.count[self.R-1][c] == 0]
    eliminationOrder.sort()

    # Transfer from candidates with fewest votes first
    ctng = self.continuing.copy()
    descTie = ""
    for i in range(len(remainingLosers)):
      (loser, desc) = self.breakWeakTie(self.R-1, remainingLosers, "fewest",
                                        "order of candidate elimination")
      descTie += desc
      eliminationOrder.append(loser)
      remainingLosers.remove(loser)
      for bi in self.votes[loser]:
        c = self.b.getTopChoiceFromBallot(bi, ctng)
        if c != None:
          self.votes[c].append(bi)
          # If receiving candidate becomes a winner, then that
          # candidate can't receive any more votes.
          if len(self.votes[c]) >= self.thresh[self.R-1]:
            ctng.remove(c)

      self.votes[loser] = []

    desc = "Count after eliminating %s and transferring votes. " % \
         self.b.joinList(eliminationOrder)
    return desc + descTie

  def postCount(self):
    "Save ballots of winners to a file so that vacancies may be filled."
    OrderDependentSTV.postCount(self)
    
    if not self.saveWinnersBallots:
      return

    self.msg.append("")
    self.msg[self.R+1] = "The winning candidates' votes are stored in the "\
                         "following files:\n"

    # Stuff used for creating a unique valid filename for each candidate
    assert(os.path.exists(self.outputDir))
    validChars = string.ascii_letters + string.digits

    # For each candidate save the candidate's ballots to a unique
    # filename that starts with the ballot file name.
    for c in self.winners:

      # Create a unique filename
      cName = self.b.names[c]
      cNameNorm = string.join((x for x in cName if x in validChars), "")
      fName = os.path.join(self.outputDir, cNameNorm + ".blt")
      i = 1
      while os.path.exists(fName):
        i += 1
        fName = os.path.join(self.outputDir, cNameNorm + str(i) + ".blt")

      self.msg[self.R+1] += "    %s -> %s\n" % (cName, fName)

      # Create a new ballots object for each winner
      candidateBallots = self.b.copy(False)
      candidateBallots.withdrawn = self.winners.copy()
      candidateBallots.numSeats = 1
      candidateBallots.title = "%s's ballots from %s" % (cName, self.b.title)

      # Copy the relevant ballots and save
      for i in self.votes[c]:
        ballot, ID = self.b.getBallotAndID(i)
        candidateBallots.appendBallot(ballot, ID)
      candidateBallots.saveAs(fName)
      del candidateBallots
