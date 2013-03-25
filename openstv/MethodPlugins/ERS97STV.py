"Plugin module for ERS97STV"

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

__revision__ = "$Id: ERS97STV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import GregorySTV
from openstv.plugins import MethodPlugin

##################################################################

class ERS97STV(GregorySTV, MethodPlugin):
  "ERS97 STV"

  methodName = "ERS97 STV"
  longMethodName = "ERS97 STV"
  status = 1

  htmlBody = """
<p>The Electoral Reform Society of Great Britian and Ireland has
issued its recommended rules for implementing the single transferable
vote.  The most recent version of its rules issued in 1997 and is
commonly referred to as the ERS97 rules.  These rules are similar to
those used in Northern Ireland and Malta.</p>

<p>The complete set of rules can be found at
http://www.electoral-reform.org.uk/votingsystems/stvrules.htm.  The
relevant portions of these rules are included below.</p>

<p>OpenSTV's implementation of the ERS97 rules has been validated
against the eSTV program, which can be found at http://www.estv.co.uk/.</p>

<hr>

<p><b>4. GENERAL DESCRIPTION OF THE COUNT</b></p>

<p>4.1 The count is divided into a number of stages. At the first stage
the voting papers are counted to determine the total vote. They are
then sorted according to their first preferences, and any papers which
are invalid are removed. The total number of valid votes is then found
and the quota calculated. Any candidates who have at least a quota of
first preference votes are deemed elected at this stage.

<p>4.2 Each subsequent stage of the count is concerned either with the
transfer of surplus votes of a candidate whose vote exceeds the quota,
or with the exclusion of one or more candidates with the fewest votes.

<p>4.3 This procedure continues until either sufficient candidates have
reached the quota to fill all the seats, or there is the same number
of candidates left as unfilled seats.

<p>4.4 These rules refer to the various forms published by the Electoral
Reform Society. The use of these forms is optional, but where they are
used, the various options should be made easier, particularly for
those not experienced in conducting STV counts.

<p>4.5 In the rules below, words in <b>bold type</b> indicate that there
is a definition in the glossary (section 6).

<p><b>5. DETAILED INSTRUCTIONS FOR THE COUNT</b>

In a public election, it is necessary to include certain formalities,
such as unsealing and opening the ballot boxes at the start, checking
the number of papers in each and ascertaining that the candidates and
their agents are content at the conclusion of each stage. For
simplicity these have been omitted from these instructions.

<p><b>5.1 First stage</b>

<p>5.1.1 Count all the voting papers to determine the total number of
votes cast.

<p>5.1.2 Sort the voting papers into <b>first preferences</b>, setting
aside any <b>invalid papers</b>. Count the number of invalid papers,
and subtract this from the total vote to get the <b>total valid
vote</b>.

<p>5.1.3 Check the sorting, and count the papers for each candidate into
bundles, inserting a <b>counting slip</b> (green) in each bundle
marked with the name of the candidate, the number of papers, and
'first stage'. For very small elections, the use of counting slips may
be dispensed with.

<p>5.1.4 Check the counting. Enter on each candidate's <b>vote record
form</b> (yellow) the total number of <b>first preference</b> votes.

<p>5.1.5 Copy the <b>candidates' votes</b> from the vote record forms
onto a <b>result sheet</b> (white), and check that their total is the
same as the total valid vote.

<p>5.1.6 Calculate the <b>quota</b> by dividing the total valid vote by one
more than the number of places to be filled. Take the division to two
decimal places. If the result is exact that is the quota. Otherwise
ignore the remainder, and add 0.01.

<p>5.1.7 Considering each candidate in turn in descending order of their
votes, <b>deem elected</b> any candidate whose vote equals or exceeds
(a) the quota, or (b) (on very rare occasions, where this is less than
the quota), the <b>total active vote</b>, divided by one more than the
number of places not yet filled, up to the number of places to be
filled, subject to paragraph 5.6.2.

<p>5.1.8 That completes the first <b>stage of the count</b>. Now proceed
to section 5.2 below.

<p><b>5.2 Subsequent stages</b>

<p>5.2.1 Each subsequent stage will involve either the distribution of a
surplus, or, if there is no surplus to distribute, the exclusion of
one or more candidates.

<p>5.2.2 If one or more candidates have <b>surpluses</b>, the largest of
these should now be transferred. However the transfer of a surplus or
surpluses is deferred and reconsidered at the next stage, if the total
of such surpluses does not exceed either:

<p>(a) The difference between the votes of the two candidates who have
the fewest votes, or

<p>(b) The difference between the total of the votes of two or more
candidates with the fewest votes who could be excluded under rule
5.2.5, and the vote of the candidate next above.

<p>5.2.3 If one or more candidates have surpluses which have not been
deferred, transfer the largest surplus. If the surpluses of two or
more candidates are equal, and they have the largest surplus, transfer
the surplus of the candidate who had the greatest vote at the first
stage or at the earliest point in the count, after the transfer of a
batch of papers, where they had unequal votes. If the votes of such
candidates have been equal at all such points, the Returning Officer
shall decide which surplus to transfer by lot.

<p>5.2.4 The transfer of a surplus constitutes a stage in the
count. Details of how to do this are in section 5.3. If, after
completing the transfer, there are still any untransferred surpluses,
and not all the places have been filled, proceed as in paragraph 5.2.2

<p>5.2.5 If, after all surpluses have been transferred or deferred, one or
more places remain to be filled, the candidate or candidates with the
fewest votes must be excluded. Exclude as many candidates together as
possible, provided that:

<p>(a) Sufficient candidates remain to fill all the remaining places

<p>(b) The total votes of these candidates, together with the total of
any deferred surpluses, does not exceed the vote of the candidate next
above.

<p>If the votes of two or more candidates are equal, and those candidates
have the fewest votes, exclude the candidate who had the fewest votes
at the first stage or at the earliest point in the count, after the
transfer of a batch of papers, where they had unequal votes. If the
votes of such candidates have been equal at all such points the
Returning Officer shall decide which candidate to exclude by lot.

<p>5.2.6 Details of how to exclude a candidate are given in section 5.4.

<p>5.2.7 Exclusion of one or more candidates constitutes a stage in the
count. If, after completing this, there are any surpluses to transfer,
and not all the places have been filled, proceed as in paragraph
5.2.2. Otherwise proceed to exclude further candidates as in paragraph
5.2.5.

<p><b>5.3 Transfer of a surplus</b>

<p>5.3.1 If a surplus arises at the first stage, select for examination
all the papers which the candidate has received.

<p>5.3.2 If a surplus arises at a later stage, because of the transfer of
another surplus or the exclusion of a candidate or candidates, select
only the last received <b>batch</b> of papers, which gave rise to the
surplus.

<p>5.3.3 Examine the selected voting papers and sort them into their
<b>next available preferences</b> for <b>continuing
candidates</b>. Set aside as <b>non-transferable papers</b> any on
which no next available preference is expressed.

<p>5.3.4 Check the sorting, count and bundle the papers now being
transferred to each candidate, also any non-transferable
papers. Insert a counting slip in each bundle marked with the stage
number, the name of the candidate to whom the papers are being
transferred, and the number of papers in the bundle.

<p>5.3.5 Count the number of transferable papers and enter the number for
each candidate on the vote record forms.

<p>5.3.6 Prepare a <b>surplus form</b> (pink). Copy the number of papers
for each candidate from the vote record forms to the surplus form, and
check the total.

<p>5.3.7 Calculate the total <b>value</b> of the <b>transferable
papers</b>. If this exceeds the surplus, determine the <b>transfer
value</b> of each paper by dividing the surplus by the number of
<b>transferable papers</b>, to two decimal places, ignoring any
remainder. If the total value does not exceed the surplus, the
transfer value of each paper is its present value.

<p>5.3.8 Calculate the value to be credited to each candidate by
multiplying the transfer value by the number of papers, check the
totals, and enter these on the surplus form.

<p>5.3.9 Copy the values to be credited, and the <b>non-transferable
difference</b> arising from the neglected remainder, from the surplus
form to the vote record forms and to the result sheet.

<p>5.3.10 Add these values to the previous votes for each candidate, and
add the non-transferable difference to the previous total of
non-transferable votes, entering the figures onto the vote record
forms and the result sheet.

<p>5.3.11 Add up the new total number of votes on the result sheet, and
check that this still equals the original total valid vote.

<p>5.3.12 Complete the counting slips with the transfer value of each
paper, and place the bundles of voting papers for each candidate with
those previously received. In a small election, where counting slips
are not being used, each ballot paper should be marked with its
transfer value.

<p>5.3.13 Considering each continuing candidate in turn in descending
order of their votes, deem elected any candidate whose vote now equals
or exceeds

<p>(a) the quota, or

<p>(b) the total active vote, divided by one more than the number of
places not yet filled, up to the number of places remaining to be
filled, subject to paragraph 5.6.2.

<p><b>5.4 Transfer of the votes of excluded candidates</b>

<p>5.4.1 Take together all the bundles of papers which are currently
credited to the candidate or candidates to be excluded, and arrange
them in batches in descending order of transfer value. Check that the
number and total value of the papers in each batch agrees with the
numbers on the vote record forms and the result sheet. Prepare an
<b>exclusion form</b> (blue).

<p>5.4.2 First, take the batch of papers with the highest transfer
value. Sort them according to the <b>next available preferences</b>
for <b>continuing candidates</b>, and set aside as <b>non-transferable
papers</b> any on which no next available preference is expressed.

<p>5.4.3 Check the sorting, count and bundle the papers for each
candidate and any non-transferable papers. Insert a counting slip in
each bundle stating the stage, the name of the candidate to whom the
papers are being transferred, the number of papers, and the transfer
value of each paper. If counting slips are not being used, the
transfer value should be marked on each paper.

<p>5.4.4 Check the counting and enter the number of papers for each
candidate and the number of non-transferable papers on the vote record
forms.

<p>5.4.5 Copy the number of papers to be transferred to each candidate
and the number of non-transferable papers, from the vote record forms
onto a column of the exclusion form, and check the total.

<p>5.4.6 Determine the total value of the papers for each candidate and
that of the non-transferable papers and check the total.

<p>5.4.7 Copy the total values for each candidate from the exclusion form
to the vote record forms, and place the bundles of voting papers for
each candidate with those previously received.

<p>5.4.8 If any papers have become non-transferable before any candidate
has been deemed elected, recalculate the quota as in paragraph 5.1.6,
ignoring the <b>non-transferable vote</b>.

<p>5.4.9 Considering each continuing candidate in turn in descending
order of their votes, deem elected any candidate whose vote now equals
or exceeds

<p>(a)the quota, or

<p>(b)the total active vote, divided by one more than the number of
places not yet filled, up to the number of places remaining to be
filled, subject to paragraph 5.6.2.

<p>5.4.10 Ensure that no further papers are given to candidates who are
no longer continuing candidates because they have been deemed to be
elected after transferring a batch of papers.

<p>5.4.11 As in paragraph 5.4.2 and subsequently, sort and transfer each
batch of papers in turn in descending order of transfer value,
complete a column of the exclusion form for each batch, and deem
candidates to be elected as appropriate.

<p>5.4.12 After all the batches of papers have been transferred, the
right hand (totals) column on the exclusion form should be completed
and these totals checked against the vote record form(s) of the
excluded candidate(s).

<p>5.4.13 Copy the total values to be credited from the exclusion form to
the vote record forms and to the result sheet, and add these to the
previous totals for each candidate.

<p>5.4.14 Copy the new vote for each candidate from the vote record forms
onto the result sheet, and the new non-transferable vote from the
exclusion forms onto the result sheet.

<p>5.4.15 Add up the new total vote on the result sheet and check that
this agrees with the original total valid vote.

<p><b>5.5 Completion of the count</b>

<p>5.5.1 If a proposed exclusion of one or more candidates would leave
only the same number of continuing candidates as there are places
remaining unfilled, all such continuing candidates shall be deemed to
be elected.

<p>5.5.2 If, at any point in the count, the number of candidates deemed to
be elected is equal to the number of places to be filled, no further
transfers of papers are made, and the remaining continuing
candidate(s) are formally excluded.

<p>5.5.3 The count is now completed.

<p>5.5.4 Declare elected all those candidates previously deemed to be
elected.

<p><b>5.6 Notes</b>

<p>5.6.1 Calculation of the total active vote may be simplified if the
<b>Count Control Form</b> (beige) is used. This form enables the
Returning Officer to keep a continuous check on the number of votes
which are required for election of a candidate at any point in the
count, by deducting the quotas (or actual votes if less) of the
candidates deemed elected, and the total of non-transferable votes,
from the total valid vote, to give the total active vote.

<p>5.6.2 If, when candidates should be deemed elected under sections
5.1.7, 5.3.13 or 5.4.9, two or more have the same number of votes, and
there are not sufficient places left for them all, then the one or
more to be deemed elected shall be selected in descending order of
votes at the first stage or at the earliest point in the count, after
the transfer of a batch of papers, where they had unequal votes. If,
however, their votes have been equal at all such points, then none of
them shall be deemed elected at that stage.

<p>5.6.3 If a re-count is conducted where a decision has been determined
by lot, and the relevant votes are still equal in the recount, the
earlier determination shall still hold.

<p>5.6.4 These rules refer to the various forms published by the Electoral
Reform Society. The use of these forms is optional, but where they are
used, the various options should be made easier.

<p><b>6. GLOSSARY OF TERMS </b> in alphabetical order

<p>6.1 <b>Batch:</b> a bundle containing all the papers of one value in a
transfer.

<p>6.2 <b>Candidate's vote:</b> the value of voting papers credited to a
candidate at any point in the count.

<p>6.3 <b>Continuing candidate:</b> a candidate not yet deemed elected or
excluded.

<p>6.4 <b>Count Control form </b>(beige): a form designed to be used to
keep a continuous note of the total active vote, and hence the vote
required for election of a candidate at any point in the count.

<p>6.5 <b>Counting slip </b>(green): a slip inserted with a bundle of
voting papers, showing the stage at which the papers are transferred,
the name of the candidate to whom they are transferred, the number of
papers in the bundle, and the transfer value of each paper.

<p>6.6 <b>Deemed elected: </b>status of a candidate who is elected subject
to formal confirmation.

<p>6.7 <b>Exclusion form </b>(blue): a form showing the distribution of
batches of papers in descending order of transfer value from one or
more excluded candidates to continuing candidates.

<p>6.8 <b>First preference:</b> this is shown by the figure "1" standing
alone against only one candidate on a voting paper; or the name or
code of a candidate entered on a voting paper as first preference.

<p>6.9 <b>Invalid paper:</b> a voting paper on which no first or only
preference is expressed, or on which any first preference is void for
uncertainty.

<p>6.10 <b>Next available preference:</b> the next <b>subsequent
preference</b> in order, passing over earlier preferences for
candidates already deemed elected or excluded. There is no next
available preference where the next sequential preference for a
continuing candidate is uncertain.

<p>6.11 <b>Non-transferable difference:</b> the difference between the
value of a surplus and the total new value of the papers transferred,
which arises from ignoring the remainder when calculating the transfer
values to two decimal places.

<p>6.12 <b>Non-transferable paper:</b> a voting paper on which no next
available preference for a continuing candidate is expressed, or on
which any next available preference is void for uncertainty.

<p>6.13 <b>Non-transferable vote:</b> the value credited as
non-transferable at any point in the count.

<p>6.14 <b>Quota:</b> the vote which, if attained by as many candidates as
there are places to be filled, leaves at most a quota for all other
candidates; the total valid vote divided by one more than the number
of places to be filled, or a lesser value calculated as in paragraph
<p>5.4.8.

<p>6.15 <b>Result sheet </b>(white): a sheet showing the vote credited to
each and every candidate, and the non-transferable vote at successive
stages of the count.

<p>6.16 <b>Stage of the count:</b> the determination of the first
preference vote for each candidate (first stage) or the transfer of a
surplus or the exclusion of a candidate, or two or more candidates at
the same time, and the transfer of their votes.

<p>6.17 <b>Subsequent preferences:</b> shown by the figures "2", "3",
etc., standing alone against different candidates on a voting paper;
or the names or codes of candidates entered in order on a voting paper
as second, third, etc., preferences.

<p>6.18 <b>Surplus:</b> the amount by which a candidate's vote exceeds the
quota.

<p>6.19 <b>Surplus form </b>(pink): A form showing the calculation of the
transfer value and the distribution of transferable papers from a
candidate deemed elected to continuing candidates.

<p>6.20 <b>Total active vote:</b> the sum of the votes credited to all
continuing candidates, plus any votes awaiting transfer.

<p>6.21 <b>Total valid vote:</b> the total number of <b>valid voting
papers</b>.

<p>6.22 <b>Transfer value:</b> the value, being unity or less, at which a
voting paper is transferred from an elected or an excluded candidate
to a continuing candidate. Where counting slips are not used, it is
recommended that this value be marked on each paper at the time of
transfer.

<p>6.23 <b>Transferable paper:</b> a voting paper which, having been
allocated to a candidate, bears a next available preference for a
continuing candidate.

<p>6.24 <b>Valid voting paper:</b> a voting paper on which a first or an
only preference is unambiguously expressed.

<p>6.25 <b>Value:</b> the value of a voting paper is unity, or a lower
value at which it was last transferred.

<p>6.26 <b>Vote record form </b>(yellow): a form showing the vote credited
to any one candidate, or showing the non-transferable vote, at
successive stages of the count.

<p><b>7. CASUAL VACANCIES</b>

<p>No purpose is served by holding a by-election, since a representative
so elected would represent the dominant opinion group in the
particular multi-member constituency, and not necessarily the opinion
group of the vacating member.  There are three possibilities:

<p>7.1 The vacancy may be filled by recounting <I>all</I> the original
voting papers for the constituency, passing over all preferences for
the vacating representative, and for any other candidate who now
withdraws. With the provision that no other previously elected
representative should be excluded, the count proceeds until a stage
when a new representative has been elected. This representative,
together with the surviving representatives, will reflect the original
wishes of the electorate. This method requires that the original
voting papers should be retained under secure conditions.

<p>7.2 The vacancy may be filled by co-option. A person could be co-opted
who reflects, as far as possible, the opinion group of the vacating
representative. The party, if any, of the vacating representative
might be invited to nominate a candidate for the elected body to
co-opt. Alternatively, the last formally excluded candidate could be
co-opted.

<p>7.3 The vacancy may be left unfilled. When a large number of
representatives has been elected together by the Single Transferable
Vote, it may be thought that the surviving representatives can
adequately represent the electorate until the next election.

"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):    
    GregorySTV.__init__(self, b)
    MethodPlugin.__init__(self)
    
    self.prec = 2
    self.weakTieBreakMethod = "forward"
    self.threshName = ["ERS97", "Dynamic", "Fractional"]
    self.delayedTransfer = "On"
    self.batchElimination = "LosersERS97"
    self.numStages = 0

  def preCount(self):
    GregorySTV.preCount(self)
    
    # Data structures needed only for ERS97 rules.
    # ERS97 rules contain stages and substages, but each of these is a round.
    # Example:
    #   R S
    #   ---
    #   1 1
    #   2 2
    #   3
    #   4 3
    # We need to compute all of the rounds but only print the stages.
    # Round 3 is a substage between stages 2 and 3.  Substages occur when
    # transferring ballots from eliminated candidate and different ballots
    # have different values.  The stage involves transferring all of the
    # ballots, but each substage involves transferring ballots of a given
    # value.
    self.quota = []
    self.S = 0
    self.stages = []    # Stores rounds for each stage
                        # [ [0] [1] [2] [3 4] [5] ... ]

  def postCount(self):
    GregorySTV.postCount(self)
    self.numStages = self.S+1
  
  def roundToStage(self, r):
    "Return the stage corresponding to a given round."
    for s in range(len(self.stages)):
      if r in self.stages[s]: 
        return s
    assert(0)

  def allocateRound(self):
    "Add quota allocation."

    GregorySTV.allocateRound(self)
    self.quota.append(0)
    # These are copied from the previous round.  Depending on the situation,
    # they will be reused or updated in place.
    if self.R > 0:
      self.quota[self.R] = self.quota[self.R-1]
      self.thresh[self.R] = self.thresh[self.R-1]

  def updateThresh(self):
    "Compute the value of the ERS97 winning threshold."

    assert(self.threshName[0] == "ERS97")
    assert(self.threshName[1] == "Dynamic")
    assert(self.threshName[2] == "Fractional")

    # The quota is recalculated at every round until there is at
    # least one winner.  Afterwards it is just repeated.
    if len(self.winners) == 0:
      quota, r = divmod(self.p*self.b.numBallots - 
                        self.exhausted[self.R],
                        self.numSeats+1)
      if r > 0: 
        quota += 1
      if self.R == 0:
        desc = "The initial quota is %s. " % self.displayValue(quota)
      else:
        desc = "Since no candidate has been elected, the quota is reduced "\
                "to %s. " % self.displayValue(quota)
      self.roundInfo[self.R]["quota"] = desc
    else:
      quota = self.quota[self.R]

    # The winning threshold changes every round.  See ERS97 rules
    # for an explanation.
    totalActiveVote = 0
    for c in self.continuing | self.losers:
      totalActiveVote += self.count[self.R][c]
    for c in self.winnersOver:
      if self.count[self.R][c] > quota:
        totalActiveVote += self.count[self.R][c] - quota
    numSeatsRemaining = self.numSeats - len(self.winners)
    if numSeatsRemaining > 0:
      thresh, r = divmod(totalActiveVote, numSeatsRemaining+1)
      if r > 0: 
        thresh += 1
    else:
      thresh = self.thresh[self.R]

    self.quota[self.R] = quota
    self.thresh[self.R] = thresh

  def updateSurplus(self):
    "Compute the threshold and surplus for current round."

    # Update surplus
    self.surplus[self.R] = 0
    for c in self.winnersOver | self.continuing:
      if self.count[self.R][c] > self.quota[self.R]:
        self.surplus[self.R] += self.count[self.R][c] - self.quota[self.R]

  def updateWinners(self):
    "Find new winning candidates."

    # ERS97 is a pain because it can happen that there is one more
    # candidate over thresh than there are spots remaining!
    # If this happens there will be a tie.

    # When there are not enough votes, thresh can go to 0.00.
    # When this happens, every remaining candidate would be a winner
    # (even those with 0 votes).  Require at least 0.01 votes to be a
    # winner.

    # count the number of winners
    if not self.roundInfo[self.R].has_key("winners"):
      self.roundInfo[self.R]["winners"] = ""
    potentialWinnersList = []
    for c in self.continuing:
      if self.count[self.R][c] >= max(self.thresh[self.R], 1):
        potentialWinnersList.append(c)

    # if there is an extra do tie breaking
    assert(len(potentialWinnersList) + len(self.winners) <= self.numSeats + 1)
    if len(potentialWinnersList) + len(self.winners) == self.numSeats + 1:
      (c, desc) = self.breakWeakTie(self.R, potentialWinnersList, "fewest",
                                     "a candidate over threshold to eliminate")
      potentialWinnersList.remove(c)
      self.roundInfo[self.R]["winners"] += desc

    # change status of all winners
    if len(potentialWinnersList) > 0:
      potentialWinnersList.sort(key=lambda a, f=self.count[self.R]: -f[a])
      self.roundInfo[self.R]["winners"] += self.newWinners(potentialWinnersList)
      self.updateThresh()
      self.updateSurplus()
      # lowered threshold could create new winners
      if len(self.winners) < self.numSeats:
        self.updateWinners()

  def sortVotesByTransferValue(self, cList):
    "Sort votes according to ERS97 rules."

    self.votesByTransferValue = {}
    for loser in cList:
      for i in self.votes[loser]:
        v = self.transferValue[i]
        if v not in self.votesByTransferValue.keys():
          self.votesByTransferValue[v] = []
        self.votesByTransferValue[v].append(i)

    self.transferValues = self.votesByTransferValue.keys()
    self.transferValues.sort(reverse=True)

  def describeRound(self, nonFinalSubstage=False):
    
    if self.roundInfo[self.R]["action"][0] == "first":
      text = "Count of first choices. "
    elif self.roundInfo[self.R]["action"][0] == "surplus":
      text = self.roundInfo[self.R]["surplus"]
    elif self.roundInfo[self.R]["action"][0] == "eliminate":
      text = self.roundInfo[self.R]["eliminate"]
      
    if self.roundInfo[self.R].has_key("quota"):
      text += self.roundInfo[self.R]["quota"]
    
    if self.roundInfo[self.R].has_key("winners"):
      text += self.roundInfo[self.R]["winners"]
      
    # Explain what will happen in the next round
    if self.electionOver() or nonFinalSubstage:
      text += ""
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

  def transferVotesFromCandidates(self, elimList):
    elimList.sort()
    nTransferValues = len(self.transferValues)
    if nTransferValues == 0:
      # This will happen when all eliminated candidates have 0 votes
      self.updateRound()
      self.updateWinners()
      self.roundInfo[self.R]["eliminate"] += \
          "Count after eliminating %s. No votes are "\
          "transferred since all eliminated candidates "\
          "have zero votes. " % self.b.joinList(elimList)
      self.describeRound()
    else:
      for i, v in enumerate(self.transferValues):
        if i != 0:
          self.R += 1
          self.allocateRound()
          self.roundInfo[self.R]["eliminate"] = ""
          self.roundInfo[self.R]["action"] = self.roundInfo[self.R-1]["action"]
          self.stages[self.S].append(self.R)
        self.roundInfo[self.R]["eliminate"] += \
            "Count after substage %d of %d of eliminating "\
            "%s. Transferred votes with value %s. "\
            % (i+1, nTransferValues, self.b.joinList(elimList),
               self.displayValue(v))
        self.transferVotesWithValue(v)
        self.updateRound()
        self.describeRound(i+1 < nTransferValues)
        if self.electionOver():
          break
